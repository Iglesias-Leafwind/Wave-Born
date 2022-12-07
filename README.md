# Wave-Born
A fun game made with pygame

# # Todo List

32x32 pixels por block in game

Limited timed side scroller per level

Infinite Levels


DONE - SOUND MECHANICS


Create folders to be organized


World generation by blocks:

-> Create a small algorithm that can whith small world blocks create a playable terrain for the player always generates 2 blocks outside the field of view

-> Create many world blocks each with pre requesits to be able to get to them

-> Each world block can be 16 in game blocks wide and use the full height of the game


Create Player:

-> walking makes sound

-> running makes more sound

-> jump start makes a sound

-> jump end makes another sound

-> every collision with anything makes a sound

-> if any enemy ability or enemy collision or he falls of the level then player dies


Create Enemies:

-> (birdlike) small flying enemy his cry is a low frequency sound

--> shoots small spheres that on impact makes sound

-> (spiderlike) small ground enemy his cry is a medium frequency sound

--> walks around and each step doesn't make a sound he is silent

--> tries to catch the player

-> (turtlelike) medium ground enemy his cry is a medium to high frequency sound

--> makes a small stomp sound when walking around

--> if he sees the player jumps in that direction even if the player is no longer there

-> (giant whale) giant flying enemy with high frequency sound

--> shouts and gets ready to fire a giant laser from its belly

--> is incredibly slow

--> when shoting the laser (divided into 128 wide in pixels) shoots until it hits a surface if one of the laser pixels hits a surface only that laser pixel goes to the top of the surface it hit, the rest stays bellow


Time out:

if time runs out a giant whale comes from behind the player at his speed + speed of a normal whale shooting a giant laser and destroying every block it hits until it reaches the player and kills him or the player reaches the end


End:

A giant futuristic flying city

-> when the player reaches the city it ends the game saving him from the time whale
