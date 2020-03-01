<a href="https://www.facebook.com/angelo.pascuzzi"><img src="https://imagizer.imageshack.com/img921/9759/BIJ337.jpg" alt="La Tavernetta"></a>

# La Tavernetta - Tavern and Pizzeria - Website

> Very simple website where users can order food and seats, Admin can manage the orders and stocks 
> Restaurant    Website    Orders    Pizzeria    CS50
- Build Status
- Example gifs


[![Build Status](http://img.shields.io/travis/badges/badgerbadgerbadger.svg?style=flat-square)](https://travis-ci.org/badges/badgerbadgerbadger)
[![Open Source Society University - Computer Science](https://img.shields.io/badge/OSSU-computer--science-blue.svg)](https://github.com/ossu/computer-science)

![Imgur GIF](https://i.imgur.com/7Akpl5K.gif)
![Imgur GIF 2](https://i.imgur.com/am51jBZ.gif)



## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)

---

## Installation

- All the `code` required to get started
- Images of what it should look like

### Clone

- Clone of the repo coming soon.

### Setup
All the dependencies:

```shell
cs50
Flask
Flask-Session
requests
```

---

## Features

### Users
- Users can register, password is protected by hash256 via werkzeug.security.
- Ability for users to log in and order meals and/or seats.
- Items are first put into basket where users can choose the collection date.
- Maximum allowed seats per day is 85, flask will take care of verifying that.
- Ability to order full room for 65 seats.
- For the basket the checkout with card is only a template, will need to be implemented for the system to be working properly.

### Admin
- Admin can choose to delete orders for the admin_orders page.
- Admin can clean the orders for dates previous than the current one automatically.
- Admin can change the number of available items at / page. (index)

### Known bugs or missing features

- Menu page will accept a value of -1 for a given item and will put it in the basket. Needs to be fixed in python.
- Admin cannot delete individual items, only entire order.
- Users cannot delete individual items from the basket, only from the menu page.
- There is no connection to any credit card service provider, needs to be implemented.

---

## Contributing

> To get started...

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone available soon.

### Step 2

- **HACK AWAY!** 🔨🔨🔨

---

## Team <br /> 


One person project. Meself. Made for CS50. <br />


---

## FAQ

- **Is the code completely optimised?**
    - No, there are many things that need to be added to this to make it completely secure and to be able to make orders. (thwart username, credit card handling etc...)

- **Does this restaurant really exist?**
    - Yes but I really doubt you'll be able to go ;).

- **Is *everything* working correctly?**
    - Only as far as  I can tell, if any errors are found feel free to contribute to the project.

---

## Support

Reach out to me at one of the following places!

- Linkedin at <a href="https://www.linkedin.com/in/angelo-pascuzzi-6128a99b/" target="_blank">`Angelo Pascuzzi`</a>
- Facebook at <a href="https://www.facebook.com/angelo.pascuzzi" target="_blank">`Angelo Pascuzzi`</a>
- Twitter at <a href="https://twitter.com/AngeloPascuzzi1" target="_blank">`@AngeloPascuzzi1`</a>
- Sample readme.md from https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46
