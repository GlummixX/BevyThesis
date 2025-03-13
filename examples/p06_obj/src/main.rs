use bevy::{
    input::mouse::MouseMotion,
    prelude::*,
    render::{
        settings::{Backends, RenderCreation, WgpuSettings},
        RenderPlugin,
    }, window::PrimaryWindow,
};
use bevy_obj::ObjPlugin;

//https://sketchfab.com/3d-models/the-utah-teapot-1092c2832df14099807f66c8b792374d

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
    app.add_plugins(ObjPlugin);
    app.add_systems(Startup, setup);
    app.add_systems(Update, camera_controller_system);
    app.add_systems(Update, esc_exit_system);
    app.run();
}

fn esc_exit_system(mut exit_events: ResMut<Events<bevy::app::AppExit>>, keyboard: Res<ButtonInput<KeyCode>>){
    if keyboard.pressed(KeyCode::Escape){
        exit_events.send(bevy::app::AppExit::Success);
    }
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
                let by = transform.rotation * input * 5.;
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
    asset_server: Res<AssetServer>,
) {
    // Create camera
    commands.spawn((Camera3d::default(), Transform::from_xyz(0., 0., 20.)));
    // Create light
    commands.spawn((
        DirectionalLight{
            shadows_enabled:true,
            illuminance: 1500.0,
            ..Default::default()
        },
        Transform::from_xyz(25.0, 30.0, 35.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));

    /*commands.spawn(SceneRoot(asset_server.load(
        GltfAssetLabel::Scene(0).from_asset("teapot.gltf"),
    )));*/

    let mesh = Mesh3d(asset_server.load("teapot.obj"));
    commands.spawn((
        mesh,
        MeshMaterial3d(materials.add(Color::srgb(1.0, 1.0, 1.0))),
        Transform::from_xyz(20., 20., 20.).with_scale(Vec3::splat(0.2)),
    ));
}
