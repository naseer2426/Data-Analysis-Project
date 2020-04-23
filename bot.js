const Discord = require("discord.js");
const child = require("child_process");
const fs = require("fs");
var CronJob = require("cron").CronJob;

const token = JSON.parse(fs.readFileSync("config.json"))["bot_config"];
console.log(token);
const client = new Discord.Client();

client.on("ready", () => {
    console.log(`Logged in as ${client.user.tag}!`);
    // setInterval(() => {
    //     const channel = client.channels.cache.get("701711183824289806");
    //     channel.send("Spook!");
    // }, 1000);
});

var myFunc;

client.on("message", (msg) => {
    if (msg.content == "status") {
        var data = fs.readFileSync("test.csv").toString();
        // console.log(data);
        data = data.split("\n");
        var unique_data = fs.readFileSync("unique_posts.csv").toString();
        unique_data = unique_data.split("\n");
        var reply = {
            unique_posts: unique_data.length,
            total_data: data.length,
        };
        msg.reply(JSON.stringify(reply));
    }
    if (msg.content == "test") {
        // var result = client.guilds
        //     .get("701711183824289802")
        //     .channels.get("701711183824289806")
        //     .send("Spook!");
    }
});

var scrape = () => {
    const channel = client.channels.cache.get("701711183824289806");
    console.log("started scrapping");
    channel.send("Scrapping session finsished");
    var stdout = child.execSync("python3 scrapper.py").toString();
    // console.log(stdout);
    // if (stdout != "success") {

    channel.send(stdout);
    // }
};

var job = new CronJob("0 0,6,12,18,24,30,36,42,48,54 * * * *", function () {
    scrape();
});
job.start();
// client.emit("message", { content: "ping" });

client.login(token);
