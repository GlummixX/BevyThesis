use bevy::{
    prelude::*,
    window::{PresentMode, WindowMode, WindowResolution},
};

fn main() {
    // Create the window
    let window_settings = Window {
        resolution: WindowResolution::new(800.0, 600.0),
        title: "P00 Window example".to_string(),
        mode: WindowMode::Windowed,
        present_mode: PresentMode::AutoVsync,
        ..default()
    };
    // Create the app
    let mut app = App::new();
    app.add_plugins(DefaultPlugins.set(WindowPlugin {
        primary_window: Some(window_settings),
        ..default()
    }));
    app.run();
}
