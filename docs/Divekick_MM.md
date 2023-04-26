# Stream Chat Wars - Divekick

## Pick a side

Use Twitch Predictions to pick your side!

You will be automatically added to Faith gang or NoFaith gang depending on
what your Prediction badge shows (which side you bet on)

If you can't use Twitch Predictions in your region, you can use
`?jointeam Faith` and `?joinTeam NoFaith` to join a team manually.
Be aware, once you join a team, you can't leave anymore! So choose wisely!

You can also use the `?myteam` command to ask the bot which team you were assinged to.

## Controls

Controlling your team's character is done through chat commands,
all of which are starting with `+`, e.g. `+dive` makes your team's character jump.

Divekick is a very simple game with only two buttons:

* `dive` (or just `d`)
* `kick` (or just `k`)

`dive` will make your character jump into the air. While in the air, `kick` will
make your character launch himself forward in a kicking motion. `kick` on the
ground will cause your character to take a step back.

Extremely simple, isn't it?

The goal of Divekick is to hit your opponent with your kicks and take them out
(one hit KO, so every kick counts)

In case the timer runs out, whoever is closer to the centerline wins the round,
so don't jump too far back in order to dodge and outsmart your opponent. It may
just make you look very dumb in the end.


## Advanced Controls

You can even chain multiple commands together.
Just write another command in the same message and they will be executed in parallel. \
Example: `+dive kick` will press both buttons at the same time and execute the
character's special ability if you have enough meter.

Pure command chaining alone has a serve limitation though: the timing of commands may be off. \
That's why commands allow you to specifiy timing parameters, in the form of
`+<command> <delay>+<duration>`, e.g. `+dive 200+50`. \
In simple language, this commands reads as
`Wait for 200 milliseconds, then press dive for 50 milliseconds`

`<delay>` and `<duration>` have to be positive integers and represent
a timing interval in milliseconds. \
Be aware, that all commands have maximum timing value that can not be exceeded
(1000 milliseconds for most commands). \
Delay and duration **both** contribute to this maximum timing value, so long delays
can reduce the durations of your actions to less than the duration you typed in your message.

If you don't need delay, then you can omit the `<delay>+` part and simply write
`+command <duration>`, e.g. `+dive 50`. \
This is a shorter, equivalent to the complete command `+right 0+300`.

On the other hand, if you **only** need delay and are fine with the standard
duration for the command, you can use `+command <delay>+`, e.g. `+dive 200+`. \
**The `+` after `200` is essential, so the bot knows that it
should interpret that number as delay and not as duration!**

>Small sidenote: It doesn't need to be `+`, you can also use `,`, `;`, `:` or
`->`. So `+dive 200,50` is the same as `+dive 200+50`!

If you chain multiple commands with delays together, the delays all start at the
time the message is received, not the end of the action of the preceding action in the chain! \
So, `+dive 120 kick 200+50` will result in pressing the dive button for 120 milliseconds,
do nothing for the next 80 milliseonds, then press the kick button for
50 milliseconds.
