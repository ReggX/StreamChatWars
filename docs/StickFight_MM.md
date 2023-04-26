# Stream Chat Wars - Stick Fight: The Game

## Pick a side

Use Twitch Predictions to pick your side!

You will be automatically added to **Faith** gang or **NoFaith** gang depending on what your Prediction badge shows (which side you bet on)

**Faith** is for all people with the blue Predicition badge.

**NoFaith** is for all people with the pink Predicition badge.

This time we will also have two additional teams: **NoBet** and **Random**.

**NoBet** is for those that can't use Predictions in their region or missed the prediction window. If your team wins, then all bets will be null and void. Don't forget to spam `No points for you pepePoint` to taunt both Faith and NoFaith gang in that case. 😉

**Random** has no human players. It selects what action to take purely based on RNG. In the case of all human teams losing against this team, Nightbot will be unleashed with the strictest settings dishing out 5 minute timeouts for the rest of the stream. 🤖 Know your place human. 🤖

## Controls

Controlling your team's character is done through chat commands, all of which are starting with `+`, e.g. `+jump` makes your team's character jump.

### Basic movement

| Command(s)                              | Result             |
|-----------------------------------------|--------------------|
| `+left` or `+l`                         | Move left          |
| `+right` or `+r`                        | Move right         |
| `+up` or `+u`                           | Lift up your arms  |
| `+jump` or `+j`                         | Jump               |
| `+hop`                                  | Hop (shorter jump) |
| `+down` or `+d` or `+duck` or `+crouch` | Crouch down        |


### Aiming

Stick Fight: The Game allows precise aim with Right Stick on the Gamepad. Since that is too complicated for Chat, Aim commands have been reduced to four basic aim commands.

| Command(s)                            | Result             |
|---------------------------------------|--------------------|
| `+aimleft` or `+aim_left` or `aiml`   | Aim left           |
| `+aimright` or `+aim_right` or `aimr` | Aim right          |
| `+aimup` or `+aim_up` or `aimu`       | Aim up             |
| `+aimdown` or `+aim_down` or `aimd`   | Aim down           |


### Basic actions

Weapons are picked up automatically by running into them.

| Command(s)                        | Result                                                  |
|-----------------------------------|---------------------------------------------------------|
| `+shoot` or `+attack` or `+fire`  | Shoot your weapon (or swing your melee weapon           |
| `+guard` or `defend` or `+shield` | Put up your shield to defend against enemy attacks.     |
| `+throw` or `yeet`                | Throw away your weapon, so you can pick up another one. |



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

>Small sidenote: It doesn't need to be `+`, you can also use `,`, `;`, `:` or `->`. So `+right 200,50` is the same as `+right 200+50`!

If you chain multiple commands with delays together, the delays all start at the time the message is received, not the end of the action of the preceding action in the chain! \
So, `+right 200 left 200+300 jump 200+300` will result in walking right for 200 milliseconds, then diagonally jump left for the next 300 milliseconds.
