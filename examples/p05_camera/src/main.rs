use bevy::{
    input::mouse::MouseMotion,
    prelude::*,
    render::{
        settings::{Backends, RenderCreation, WgpuSettings},
        RenderPlugin,
    },
};

fn main() {
    let render_plugin = RenderPlugin {
        render_creation: RenderCreation::Automatic(WgpuSettings {
            backends: Some(Backends::VULKAN),
            ..default()
        }),
        ..default()
    };
    let mut app = App::new();
    app.add_plugins(DefaultPlugins.set(render_plugin));
    app.add_systems(Startup, setup);
    app.add_systems(Update, camera_controller_system);
    app.run();
}

fn camera_controller_system(
    mut query: Query<&mut Transform, With<Camera3d>>,
    time: Res<Time>,
    keyboard: Res<ButtonInput<KeyCode>>,
    mut mouse: EventReader<MouseMotion>,
) {
    if let Ok(mut transform) = query.get_single_mut() {
        let mut input = Vec3::ZERO;
        if keyboard.pressed(KeyCode::KeyW) {
            input.z -= time.delta_secs();
        }
        if keyboard.pressed(KeyCode::KeyS) {
            input.z += time.delta_secs();
        }
        if keyboard.pressed(KeyCode::KeyA) {
            input.x -= time.delta_secs();
        }
        if keyboard.pressed(KeyCode::KeyD) {
            input.x += time.delta_secs();
        }
        if keyboard.pressed(KeyCode::Space) {
            input.y += time.delta_secs();
        }
        if keyboard.pressed(KeyCode::KeyC) {
            input.y += time.delta_secs();
        }
        if input != Vec3::ZERO {
            let by = transform.rotation * input;
            transform.translation += by;
        }
        for ev in mouse.read() {
            let delta = ev.delta * 0.2;
            // Yaw
            let up = transform.rotation * Vec3::Y;
            let yaw: Quat = Quat::from_axis_angle(up, -delta.x.to_radians());
            // Pitch
            let right = transform.rotation * Vec3::X;
            let pitch_rotation = Quat::from_axis_angle(right, -delta.y.to_radians());
            // Apply pitch with clamping to prevent flipping
            let current_rotation = transform.rotation * pitch_rotation;
            let current_pitch = current_rotation.to_euler(EulerRot::XYZ).0;
            let clamped_pitch = current_pitch.clamp(-1.5708, 1.5708); // -90° to +90° in radians

            let current_rotation = transform.rotation * yaw;
            let current_yaw = current_rotation.to_euler(EulerRot::XYZ).1;
     
            transform.rotation = Quat::from_euler(EulerRot::XYZ, clamped_pitch, current_yaw, 0.0);
        }
    }
}

/// set up a simple 3D scene
fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    // Create camera
    commands.spawn((Camera3d::default(), Transform::from_xyz(-10., 10., 10.)));
    // Create light
    commands.spawn((
        PointLight {
            shadows_enabled: true,
            ..default()
        },
        Transform::from_xyz(25.0, 25.0, 25.0),
    ));

    // Sphere
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(5.))),
        MeshMaterial3d(materials.add(Color::srgb(1.0, 1.0, 1.0))),
        Transform::from_xyz(0., 0., 0.),
    ));
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(5.))),
        MeshMaterial3d(materials.add(Color::srgb(1.0, 0.0, 0.0))),
        Transform::from_xyz(10., 0., 0.),
    ));
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(5.))),
        MeshMaterial3d(materials.add(Color::srgb(0.0, 1.0, 0.0))),
        Transform::from_xyz(0., 10., 0.),
    ));
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(5.))),
        MeshMaterial3d(materials.add(Color::srgb(0.0, 0.0, 1.0))),
        Transform::from_xyz(0., 0., 10.),
    ));
}
