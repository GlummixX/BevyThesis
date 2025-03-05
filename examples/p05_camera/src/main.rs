use bevy::{
    input::mouse::MouseMotion,
    prelude::*,
    render::{
        settings::{Backends, RenderCreation, WgpuSettings},
        RenderPlugin,
    }, window::PrimaryWindow,
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
    primary_window: Query<&Window, With<PrimaryWindow>>,
) {
    if let Ok(window) = primary_window.get_single() {
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
                let (mut azim, mut zeni, _) = transform.rotation.to_euler(EulerRot::YXZ);
                let win_size = window.width().min(window.height());
                zeni -= (100. * ev.delta.y / win_size).to_radians();
                azim -= (100. * ev.delta.x / win_size).to_radians();
                zeni = zeni.clamp(-1.54, 1.54);

                transform.rotation =
                    Quat::from_axis_angle(Vec3::Y, azim) * Quat::from_axis_angle(Vec3::X, zeni)
            }      
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
        Mesh3d(meshes.add(Sphere::new(3.))),
        MeshMaterial3d(materials.add(Color::srgb(1.0, 1.0, 1.0))),
        Transform::from_xyz(0., 0., 0.),
    ));
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(3.))),
        MeshMaterial3d(materials.add(Color::srgb(1.0, 0.0, 0.0))),
        Transform::from_xyz(10., 0., 0.),
    ));
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(3.))),
        MeshMaterial3d(materials.add(Color::srgb(0.0, 1.0, 0.0))),
        Transform::from_xyz(0., 10., 0.),
    ));
    commands.spawn((
        Mesh3d(meshes.add(Sphere::new(3.))),
        MeshMaterial3d(materials.add(Color::srgb(0.0, 0.0, 1.0))),
        Transform::from_xyz(0., 0., 10.),
    ));

    // Box
    commands.spawn((
        Mesh3d(meshes.add(Cuboid::new(5., 5., 5.))),
        MeshMaterial3d(materials.add(Color::srgb(1.0, 1.0, 1.0))),
        Transform::from_xyz(25., 25., 25.),
    ));
}
