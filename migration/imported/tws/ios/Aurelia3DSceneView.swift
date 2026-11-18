import SwiftUI
import SceneKit
import UIKit
import QuartzCore

/// A real offline, articulated SceneKit 3D preview (not a rendered 2D sprite).
/// Prefers a bundled, artist-reviewed Aurelia.scn/USDZ asset when supplied.
/// Until then, builds a self-contained geometric 3D mannequin with moving
/// wings, head/eyes, halo and authored emotion direction. The existing richer
/// 2D portrait is always available through the view switch.
struct Aurelia3DSceneView: UIViewRepresentable {
    let wings: Int
    let tone: String
    let setting: String
    let reduceMotion: Bool
    let isForeground: Bool
    let thermalLimited: Bool
    let onPerformanceFallback: (AureliaPressureReason) -> Void

    final class Coordinator {
        let monitor = AureliaRuntimeMonitor()
        var lastWings = -1
        var lastTone = ""
        var lastSetting = ""
        var lastReduced = false
        var lastForeground = false
        var lastThermalLimited = false
        var initialized = false
        var importedClips: AureliaImportedClipDriver?
        var lastClip: AureliaMotionClip?
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView(frame: .zero)
        let art = AureliaSceneFactory.make()
        view.scene = art.scene
        context.coordinator.importedClips = art.clips
        context.coordinator.monitor.onPressure = onPerformanceFallback
        view.delegate = context.coordinator.monitor
        view.backgroundColor = UIColor(
            red: 0.08, green: 0.09, blue: 0.19, alpha: 1)
        // Lower the renderer's work on battery saver without changing
        // the companion, earned wings, motion accessibility or progression.
        let lowPower = thermalLimited ||
            ProcessInfo.processInfo.isLowPowerModeEnabled
        view.preferredFramesPerSecond = lowPower ? 30 : 60
        view.antialiasingMode = lowPower ? .none : .multisampling4X
        view.autoenablesDefaultLighting = false
        view.allowsCameraControl = true
        view.rendersContinuously = !reduceMotion && isForeground
        view.isPlaying = !reduceMotion && isForeground
        configure(view, context: context, force: true)
        return view
    }

    func updateUIView(_ view: SCNView, context: Context) {
        context.coordinator.monitor.onPressure = onPerformanceFallback
        configure(view, context: context, force: false)
    }

    static func dismantleUIView(_ view: SCNView, coordinator: Coordinator) {
        // Do not leave authored animations rendering behind a dismissed view.
        coordinator.monitor.setMonitoring(false)
        coordinator.monitor.onPressure = nil
        view.delegate = nil
        coordinator.importedClips?.stopAll()
        coordinator.importedClips = nil
        view.isPlaying = false
        view.rendersContinuously = false
        view.scene = nil
    }

    private func configure(
        _ view: SCNView, context: Context, force: Bool
    ) {
        // Inactive/background scenes behave like Reduce Motion. On return
        // to foreground the same authored clip restarts from a known pose.
        let suppressMotion = reduceMotion || !isForeground
        let state = AureliaVisualState(
            tone: tone, place: setting,
            wings: wings, reduceMotion: suppressMotion)
        let motion = AureliaMotionPlan.forScene(
            tone: tone, earnedWings: state.wings,
            reduceMotion: suppressMotion)
        let coordinator = context.coordinator
        guard force || !coordinator.initialized ||
            coordinator.lastWings != state.wings ||
            coordinator.lastTone != tone ||
            coordinator.lastSetting != setting ||
            coordinator.lastReduced != suppressMotion ||
            coordinator.lastForeground != isForeground ||
            coordinator.lastThermalLimited != thermalLimited else { return }

        let firstFrame = !coordinator.initialized
        let previousClip = coordinator.lastClip
        coordinator.initialized = true
        coordinator.lastClip = motion.clip
        coordinator.lastWings = state.wings
        coordinator.lastTone = tone
        coordinator.lastSetting = setting
        coordinator.lastReduced = suppressMotion
        coordinator.lastForeground = isForeground
        coordinator.lastThermalLimited = thermalLimited

        // Apply power-saving configuration whenever SwiftUI revisits the
        // renderable. The safety policy still measures actual frame cadence.
        let lowPower = thermalLimited ||
            ProcessInfo.processInfo.isLowPowerModeEnabled
        view.preferredFramesPerSecond = lowPower ? 30 : 60
        view.antialiasingMode = lowPower ? .none : .multisampling4X
        coordinator.monitor.setMonitoring(state.shouldAnimate)
        view.isPlaying = state.shouldAnimate
        view.rendersContinuously = state.shouldAnimate
        SCNTransaction.begin()
        SCNTransaction.animationDuration = AureliaAnimationTiming.poseDuration(
            from: previousClip, to: motion.clip,
            reduceMotion: suppressMotion, firstFrame: firstFrame)
        SCNTransaction.animationTimingFunction =
            CAMediaTimingFunction(name: .easeInEaseOut)
        guard let scene = view.scene else {
            SCNTransaction.commit()
            return
        }
        let root = scene.rootNode
        coordinator.importedClips?.select(
            motion.clip, reduceMotion: suppressMotion)
        // Imported rig players control their own skeletal and facial tracks.
        // Avoid overriding them with procedural poses.
        if coordinator.importedClips == nil {
        let face = AureliaFacialPose.forExpression(state.expression)
        let eyeScale = face.eyeOpenness
        for side in ("L", "R") {
            if let eye = root.childNode(
                withName:"Eye_" + side,recursively:true) {
                eye.removeAction(forKey:"naturalBlink")
                eye.scale = SCNVector3(1,eyeScale,1)
                if state.shouldAnimate && motion.blinkInterval > 0 {
                    let blink = SCNAction.customAction(duration:0.20) {
                        target, elapsed in
                        let t=Float(elapsed/0.20)
                        let fold=max(0.08,1.0-0.92*(1.0-abs(2*t-1.0)))
                        target.scale=SCNVector3(1,eyeScale*fold,1)
                    }
                    let action=SCNAction.repeatForever(.sequence([
                        .wait(duration:motion.blinkInterval),blink
                    ]))
                    eye.runAction(action,forKey:"naturalBlink")
                }
            }
        }
        for side in ("L", "R") {
            if let brow = root.childNode(
                withName: "Brow_" + side, recursively: true) {
                let sign: Float = side == "L" ? -1 : 1
                brow.position.y = 0.21 + face.browOffset
                brow.eulerAngles.z = sign * face.browAngle
            }
        }
        if let head = root.childNode(
            withName:"Aurelia_HeadPivot",recursively:true) ??
            root.childNode(withName:"Head",recursively:true) {
            head.eulerAngles.z=motion.headTilt
        }
        for side in ("L", "R") {
            if let arm = root.childNode(
                withName: "Arm_" + side, recursively: true) {
                arm.eulerAngles.z = side == "R"
                    ? motion.armAngle : -motion.armAngle * 0.55
            }
        }
        if let mouth = root.childNode(withName: "Aurelia_Mouth",
                                      recursively: true) {
            mouth.eulerAngles.z = face.smileTilt
            mouth.scale.x = face.mouthWidth
            mouth.scale.y = face.mouthHeight
        }
        }
        // One entitlement gate controls both procedural parent pairs and all
        // imported Blender bone / individual feather nodes. Art cannot
        // overrule the authenticated RPG wing count.
        root.enumerateChildNodes { node, _ in
            guard let name = node.name,
                  let wing = AureliaWingGate.pair(named: name) else { return }
            node.isHidden = AureliaWingGate.shouldHide(
                named: name, earnedWings: state.wings)
            node.removeAction(forKey: "naturalFlutter")
            if AureliaWingGate.isProceduralPair(named: name) &&
               coordinator.importedClips == nil {
                // Always restart flutter from its rest pose. Repeatedly
                // interrupting rotateBy otherwise accumulates wing drift.
                node.eulerAngles.z = 0
            }
            if coordinator.importedClips == nil &&
               !node.isHidden && state.shouldAnimate &&
               motion.wingFlutter > 0 &&
               AureliaWingGate.isProceduralPair(named: name) {
                let sign: CGFloat = wing.side == "l" ? -1 : 1
                let amount = CGFloat(motion.wingFlutter) * sign
                let open = SCNAction.rotateBy(
                    x: 0, y: 0, z: amount, duration: 1.7)
                let close = SCNAction.rotateBy(
                    x: 0, y: 0, z: -amount, duration: 1.7)
                open.timingMode = .easeInEaseOut
                close.timingMode = .easeInEaseOut
                let action = SCNAction.repeatForever(.sequence([open, close]))
                node.runAction(action, forKey: "naturalFlutter")
            }
        }
        let environment = AureliaSceneArt.forPlace(setting)
        let tint: UIColor
        switch environment.palette {
        case "ember": tint = UIColor(red:.27,green:.11,blue:.13,alpha:1)
        case "verdant": tint = UIColor(red:.08,green:.24,blue:.22,alpha:1)
        case "amethyst": tint = UIColor(red:.17,green:.12,blue:.34,alpha:1)
        case "gold": tint = UIColor(red:.29,green:.21,blue:.13,alpha:1)
        default: tint = UIColor(red:.09,green:.12,blue:.29,alpha:1)
        }
        view.backgroundColor = tint

        if coordinator.importedClips == nil,
           let character = root.childNode(withName:"Aurelia_Root",
                                           recursively:true) {
            character.removeAction(forKey:"idle")
            character.position = SCNVector3(0, 0, 0)
            if state.shouldAnimate && motion.hoverHeight > 0 {
                // Absolute, closed-loop hover avoids accumulating position
                // when the user changes tone or Reduce Motion mid-cycle.
                let altitude = motion.hoverHeight
                let hover = SCNAction.customAction(
                    duration: AureliaAnimationTiming.hoverCycle
                ) { target, elapsed in
                    let height = AureliaAnimationTiming.hoverOffset(
                        elapsed: Double(elapsed), amplitude: altitude)
                    target.position = SCNVector3(0, height, 0)
                }
                character.runAction(.repeatForever(hover), forKey: "idle")
            }
        }
        SCNTransaction.commit()
    }
}

private enum AureliaSceneFactory {
    static func make() -> (scene: SCNScene, clips: AureliaImportedClipDriver?) {
        if let art = bundledArt() {
            ensureCameraAndLights(art.scene)
            return art
        }
        return (scene: procedural(), clips: nil)
    }

    private static func bundledArt() ->
        (scene: SCNScene, clips: AureliaImportedClipDriver)? {
        // M017: no scene may be loaded solely because it happens to be
        // present in the app bundle. Require an explicit review manifest
        // naming the exact bytes, then inspect real native SceneKit content.
        guard let file = AureliaNativeAssetGate.reviewedScene(),
              let scene = try? SCNScene(url: file, options: nil) else {
            return nil
        }
        // Converted art must retain a real 44-bone skinner, ten facial
        // targets, twelve wing feather meshes and six authored clips.
        // A static file bearing the right names is not enough.
        guard AureliaNativeRigInspector.accepts(scene),
              let clips = AureliaImportedClipDriver(scene: scene) else {
            return nil
        }
        return (scene: scene, clips: clips)
    }

    private static func material(
        _ color: UIColor,
        metallic: CGFloat = 0,
        roughness: CGFloat = 0.5,
        emission: UIColor? = nil
    ) -> SCNMaterial {
        let mat = SCNMaterial()
        mat.lightingModel = .physicallyBased
        mat.diffuse.contents = color
        mat.metalness.contents = metallic
        mat.roughness.contents = roughness
        if let emission {
            mat.emission.contents = emission
        }
        mat.isDoubleSided = true
        return mat
    }

    private static func node(
        _ name: String,
        geometry: SCNGeometry,
        material: SCNMaterial,
        position: SCNVector3,
        scale: SCNVector3 = SCNVector3(1,1,1)
    ) -> SCNNode {
        geometry.materials = [material]
        let result = SCNNode(geometry:geometry)
        result.name = name
        result.position = position
        result.scale = scale
        return result
    }

    private static func procedural() -> SCNScene {
        let scene = SCNScene()
        let root = SCNNode()
        root.name="Aurelia_Root"
        scene.rootNode.addChildNode(root)

        let skin=material(UIColor(red:.96,green:.76,blue:.68,alpha:1))
        let hair=material(UIColor(red:.15,green:.11,blue:.34,alpha:1),
                          roughness:0.30)
        let hairLight=material(UIColor(red:.32,green:.25,blue:.60,alpha:1))
        let silk=material(UIColor(red:.86,green:.85,blue:.99,alpha:1),
                          roughness:0.35)
        let lavender=material(UIColor(red:.43,green:.35,blue:.72,alpha:1))
        let pearl=material(UIColor(red:.85,green:.92,blue:1,alpha:1),
                           roughness:0.28,
                           emission:UIColor(red:.08,green:.12,blue:.25,alpha:1))
        let iris=material(UIColor(red:.25,green:.57,blue:.82,alpha:1),
                          roughness:0.18)
        let dark=material(UIColor(red:.11,green:.08,blue:.21,alpha:1))
        let gold=material(UIColor(red:.98,green:.77,blue:.39,alpha:1),
                          metallic:0.65,roughness:0.20,
                          emission:UIColor(red:.25,green:.13,blue:.05,alpha:1))

        root.addChildNode(node(
            "Dress",geometry:SCNCone(topRadius:.13,bottomRadius:.40,height:1.12),
            material:silk,position:SCNVector3(0,.65,0)))
        root.addChildNode(node(
            "Gown_Collar",geometry:SCNSphere(radius:.20),
            material:lavender,position:SCNVector3(0,1.31,0),
            scale:SCNVector3(1,.53,.80)))
        root.addChildNode(node(
            "Neck",geometry:SCNCylinder(radius:.056,height:.16),
            material:skin,position:SCNVector3(0,1.51,0)))
        root.addChildNode(node(
            "Hair_Back",geometry:SCNSphere(radius:.176),
            material:hair,position:SCNVector3(0,1.66,.067),
            scale:SCNVector3(1.02,1.75,.84)))
        root.addChildNode(node(
            "Head",geometry:SCNSphere(radius:.155),
            material:skin,position:SCNVector3(0,1.78,-.012),
            scale:SCNVector3(.88,1.24,.91)))
        root.addChildNode(node(
            "Hair_Crown",geometry:SCNSphere(radius:.169),
            material:hair,position:SCNVector3(0,1.923,.015),
            scale:SCNVector3(.98,.42,.95)))

        for side in ("L","R") {
            let sign: Float = side == "L" ? -1 : 1
            let eye=node(
                "Eye_" + side, geometry:SCNSphere(radius:.019),
                material:iris,
                position:SCNVector3(sign*.055,1.795,-.143),
                scale:SCNVector3(1,1,.32))
            root.addChildNode(eye)
            root.addChildNode(node(
                "Brow_" + side,
                geometry: SCNBox(width: .068, height: .012, length: .012,
                                 chamferRadius: .005),
                material: hair,
                position: SCNVector3(sign * .055, 1.840, -.133)))
            root.addChildNode(node(
                "Arm_" + side,
                geometry:SCNCapsule(capRadius:.063,height:.45),
                material:lavender,
                position:SCNVector3(sign*.31,1.15,0)))
            root.addChildNode(node(
                "Hand_" + side,
                geometry:SCNSphere(radius:.051),
                material:skin,
                position:SCNVector3(sign*.35,.92,-.015)))
            for strand in 0..<5 {
                root.addChildNode(node(
                    "Hair_" + side + "_" + String(strand),
                    geometry:SCNCapsule(capRadius:.026,height:.40),
                    material:strand % 3 == 0 ? hairLight : hair,
                    position:SCNVector3(
                        sign*(.135 + Float(strand)*.013),
                        1.69-Float(strand)*.037,.06)))
            }
            for index in 1...6 {
                let featherPair=SCNNode()
                featherPair.name=String(format:"wing_%@_%02d",side,index)
                featherPair.position=SCNVector3(
                    sign*.18,1.32+Float(index)*.042,.10)
                let n=9
                for feather in 0..<n {
                    let f=Float(feather)
                    let featherNode=node(
                        "feather_" + String(feather),
                        geometry:SCNSphere(radius:.073),
                        material:feather.isMultiple(of:3) ? pearl : silk,
                        position:SCNVector3(
                            sign*(.24+f*.10),
                            (f-3.4)*.045, .10+f*.012),
                        scale:SCNVector3(1.65,.36,.31))
                    featherNode.eulerAngles.z = sign*(0.15+f*.07)
                    featherPair.addChildNode(featherNode)
                }
                root.addChildNode(featherPair)
                // Motion starts only through the authored motion plan,
                // which also respects Reduce Motion.
            }
        }

        root.addChildNode(node(
            "Aurelia_Mouth",geometry:SCNSphere(radius:.026),
            material:dark,
            position:SCNVector3(0,1.706,-.148),
            scale:SCNVector3(1,.16,.23)))
        root.addChildNode(node(
            "Halo", geometry:SCNTorus(ringRadius:.21,pipeRadius:.009),
            material:gold,position:SCNVector3(0,2.10,0)))

        // Parent facial features/hair/halo to a head pivot, retaining
        // world-space rest coordinates. A gentle nod then moves the whole
        // face, unlike rotating a face sphere independently of its eyes.
        let headPivot=SCNNode()
        headPivot.name="Aurelia_HeadPivot"
        headPivot.position=SCNVector3(0,1.63,0)
        for child in Array(root.childNodes) {
            guard let name=child.name else { continue }
            if name=="Head" || name=="Hair_Back" ||
               name=="Hair_Crown" || name=="Aurelia_Mouth" ||
               name=="Halo" || name.hasPrefix("Eye_") ||
               name.hasPrefix("Brow_") || name.hasPrefix("Hair_") {
                let rest=child.position
                child.removeFromParentNode()
                child.position=SCNVector3(rest.x,rest.y-1.63,rest.z)
                headPivot.addChildNode(child)
            }
        }
        root.addChildNode(headPivot)

        let platform=node(
            "Sanctuary_Platform",
            geometry:SCNCylinder(radius:1.18,height:.07),
            material:material(UIColor(red:.16,green:.17,blue:.32,alpha:1)),
            position:SCNVector3(0,-.025,0))
        scene.rootNode.addChildNode(platform)
        ensureCameraAndLights(scene)
        return scene
    }

    private static func ensureCameraAndLights(_ scene: SCNScene) {
        if scene.rootNode.childNodes(passingTest:{ node, _ in
            node.camera != nil
        }).isEmpty {
            let camera=SCNNode()
            camera.camera=SCNCamera()
            camera.camera?.zNear=0.01
            camera.camera?.zFar=100
            camera.position=SCNVector3(0,1.18,3.45)
            camera.look(at:SCNVector3(0,1.05,0))
            scene.rootNode.addChildNode(camera)
        }
        if scene.rootNode.childNodes(passingTest:{ node, _ in
            node.light != nil
        }).isEmpty {
            let ambient=SCNNode()
            ambient.light=SCNLight()
            ambient.light?.type = .ambient
            ambient.light?.color=UIColor(white:0.36,alpha:1)
            scene.rootNode.addChildNode(ambient)

            let key=SCNNode()
            key.light=SCNLight()
            key.light?.type = .omni
            key.light?.intensity = 1400
            key.position=SCNVector3(-2.8,4,4)
            scene.rootNode.addChildNode(key)

            let rim=SCNNode()
            rim.light=SCNLight()
            rim.light?.type = .omni
            rim.light?.intensity = 840
            rim.position=SCNVector3(2.2,2.6,-2.2)
            scene.rootNode.addChildNode(rim)
        }
    }
}
