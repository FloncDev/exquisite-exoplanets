# Exquisite Exoplanets
The exquisite exoplanets attempted to create an idle game where you can explore planets, solve programming challanges to mine resources, and expand your space business. Sadly we only managed to complete some basic features such as account creation and core game logic.

## How to Run
Firstly, you need to setup an `.env` file

```shell
DISCORD_TOKEN=
DATABASE=sqlite:///data.sqlite

# Use the following if using docker compose, otherwise make sure to change it to your local configuration.
API_URL=http://api:80  
```
After that, the simplest way is with docker. Simply run `docker compose up -d`, then the bot and api _should_ automagiclly start.

## How to Use
After starting the bot and heading to discord, you should be able to see all the available commands after you type `/` in the discord chat. Sadly we did not have enough time to implement everything we wanted to, so the only things you are able to do are company management (found under the `/company` group), and viewing information about your profile `/profile`. We do have `/shop` working (trust me), but it will not show anything unless you manually add items via the API - so just pretend it isnt there :)

Don't forget the obligatory `/ping` command, we can guarantee that one will work ;)

## Connection to Theme
In it's current state, there isn't much connection to the theme. Our idea was to have the programming challanges involve large amounts of data, similar to advent of code.

## Contributors
Even though we did not manage to accomplish our goal, _huge_ thanks to everyone on the team for their effort, ideas, and support.

<!-- Alphabetical Order :) -->
[@Elektriman](https://github.com/Elektriman) Core game logic and game design<br>
[@Evorage0](https://github.com/Evorage0) API implementation and design<br>
[@FloncDev](https://github.com/FloncDev) Discord interaction<br>
[@MilaDog](https://github.com/MilaDog) Database and API implementation<br>
[@i-am-unknown-81514525](https://github.com/i-am-unknown-81514525) API wrapper
