var my_target = document.getElementById("target");
console.log(target);

var followers = my_target.children;

var links = []
console.log(followers.length);
for (var i = 0; i<followers.length; i++){
    var curr_follower = followers[i];
    // console.log(curr_follower);
    

    var link = "https://www.instagram.com/"+curr_follower.getElementsByClassName("FPmhX notranslate  _0imsa ")[0].title;
    
    links.push(link);
}
console.log(links.length);
console.log(JSON.stringify(links));
