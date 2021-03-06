This is addon is a **work in progress** and can't be used as-is in Blender for produciton use.

![demo](https://blenderartists.org/uploads/default/original/4X/e/a/9/ea9dd3b634f92a891d6afd0f069e71de93830a68.gif)

See the addon [thread on blenderartists.org](https://blenderartists.org/t/a-gamepad-camera-layout-tool/1240370).

# Development

To edit and run the addon, I'm using the [Blender Development addon](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) developped by Jacques Lucke.

Simply open the project in Visual Studio Code then do `CTRL + SHIFT + P` > `Blender: Run`.

The most important script of this addon is `gamepads/xbox_gamepad.py`.

# Usage

Once you loaded the addon, there is 2 operators available. Press `F3` and type `xbox` to see them.

Start with the `Diagnostic XBOX controller` to see if your xbox inputs are correctly detected.

The `Control camera with XBOX controller` is a complete work in progress and is still buggy. Before running it, change the viewport view to the camera `F3 > View Camera` or simply press `Numpad 0`. After that, start the operator, select the camera, press play and move the gamepad's joysticks.

# Limitations

The first and biggest limitation is that Blender doesn't get updated when we use the gamepad. At the opposite, moving the mouse or pressing a key trigger an update in Blender and all the running operators will be notified. Because of this, getting the gamepad at the correct time is very tricky.

To fix this, we need to play the animation in blender to get a regular update each frame and process the gamepad inputs. But the movements can be very steppy with a low framerate.

# References

- [https://blenderartists.org/t/working-on-a-gamepad-camera-layout-tool-prototype/1240370](https://blenderartists.org/t/working-on-a-gamepad-camera-layout-tool-prototype/1240370)
- [https://github.com/kevinhughes27/TensorKart/blob/master/utils.py](https://github.com/kevinhughes27/TensorKart/blob/master/utils.py)
- [https://i.redd.it/hrr79vpb0m601.png](https://i.redd.it/hrr79vpb0m601.png)
- [https://developer.blender.org/D7812](https://developer.blender.org/D7812)
- [https://www.youtube.com/watch?v=a7qyW1G350g&t=482s](https://www.youtube.com/watch?v=a7qyW1G350g&t=482s)
- [https://github.com/zeth/inputs](https://github.com/zeth/inputs)