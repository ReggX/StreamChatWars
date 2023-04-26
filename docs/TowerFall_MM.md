# Stream Chat Wars - TowerFall Ascension

## Controls

Controlling your team's character is done through chat commands,
all of which are starting with `+`, e.g. `+right` makes your team's character go right.


### Basic movement

| Command(s)                              | Result             |
|-----------------------------------------|--------------------|
| `+left` or `+l`                         | Move left          |
| `+right` or `+r`                        | Move right         |
| `+up` or `+u`                           | Aim upwards        |
| `+down` or `+d` or `+duck` or `+crouch` | Crouch down        |
| `+jump` or + `+j`                       | Jump               |


### Basic actions

| Command(s)                                         | Result                                                                   |
|----------------------------------------------------|--------------------------------------------------------------------------|
| `+shoot` or `+attack` or `+fire`                   | Shoot your bow.                                                          |
| `+alt` or `altshoot` or `+altattack` or `+faltire` | Trigger your alt action (like detonating bomb arrows), behaves like `shoot` if you have no alt action available. |
| `+toggle` or `+switch`              | Change the currently selected arrow type (if you have different arrows) |


### Advanced movement

| Command(s)                      | Result                                                                      |
|---------------------------------|-----------------------------------------------------------------------------|
| `+dodge` or `+dash` while holding a direction key | Dash in the selected direction, dodging enemy arrows. Best used in combination like `+right dash` |


## Advanced Controls

You can even chain multiple commands together.
Just write another command in the same message and they will be executed in parallel. \
Example: `+left jump` will result in a diagonal jump in the left direction.

Pure command chaining alone has a serve limitation though: the timing of commands may be off. \
That's why commands allow you to specifiy timing parameters, in the form of `+<command> <delay>+<duration>`, e.g. `+right 200+300`. \
In simple language, this commands reads as `Wait for 200 milliseconds, then press right for 300 milliseconds`

`<delay>` and `<duration>` have to be positive integers and represent a timing interval in milliseconds. \
Be aware, that all commands have maximum timing value that can not be exceeded (1000 milliseconds for most commands). \
Delay and duration **both** contribute to this maximum timing value, so long delays can reduce the durations of your actions to less than the duration you typed in your message.

If you don't need delay, then you can omit the `<delay>+` part and simply write `+command <duration>`, e.g. `+right 300`. \
This is a shorter, equivalent to the complete command `+right 0+300`.

On the other hand, if you **only** need delay and are fine with the standard duration for the command, you can use `+command <delay>+`, e.g. `+right 200+`. \
**The `+` after `200` is essential, so the bot knows that it should interpret that number as delay and not as duration!**

>Small sidenote: It doesn't need to be `+`, you can also use `,`, `;`, `:` or `->`. So `+right 100,300` is the same as
`+right 100+300`!

If you chain multiple commands with delays together, the delays all start at the time the message is received, not the end of the action of the preceding action in the chain! \
So, `+right 200 left 200+300 jump 200+300` will result in walking right for 200 milliseconds, then diagonally jump left for the next 300 milliseconds.


### Examples

| Input                     | Result                                                                                                                              |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `+right 500`              | Hold the right key for `500` milliseconds. milliseconds                                                                                            |
| `+right 500 dash 200+` | Like before, start walking, but this time after `200` milliseconds of delay, execute a dash move |
