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
    app.run();
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
        Mesh3d(meshes.add(Cube::new(5.))),
        MeshMaterial3d(materials.add(Color::srgb(1.0, 1.0, 1.0))),
        Transform::from_xyz(0., 0., 0.),
    ));
}
