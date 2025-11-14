# Our Corner

Our Corner is a mini social platform built for small local communities. It provides numerous ways for the community to interact, including a post feed to share thoughts, an events section to get involved, and a marketplace to trade with your locals.

![Our Corner shown on a range of devices](/readme-docs/devices-showcase.png)

[View Our Corner on Heroku](https://hackathon-social-platform-0d4a6cd4eda3.herokuapp.com/)

## CONTENTS

* [Purpose and Value](#Purpose-and-Value)
  * [Application Purpose](#Application-Purpose)
  * [User Value](#User-Value)

* [Design](#Design)
  * [Colour Scheme](#Colour-Scheme)
  * [Typography](#Typography)
  * [Page Layout](#Page-Layout)
  * [Database Structure](#Database-Structure)
  * [Features](#Features)
  * [Accessibility](#Accessibility)

* [Technologies Used](#Technologies-Used)
  * [Languages Used](#Languages-Used)
  * [Frameworks, Libraries & Programs Used](#Frameworks-Libraries--Programs-Used)

* [Deployment](#Deployment)

* [Testing](#Testing)
  * [Manual Functionality Testing](#Manual-Functionality-Testing)
  * [Device Responsivity Testing](#Device-Responsivity-Testing)

* [Validation](#Validation)

* [AI Usage](#AI-Usage)

* [Credits](#Credits)

- - -

## Purpose and Value

### Application Purpose

This application is designed to give small local communities a platform on which they can interact with each other in a number of ways. The main use cases would be: a feed section for viewing, submitting, and commenting on posts; an events section to find out about and get involved in events in the local area; and a marketplace section for listing items for sale and joining auctions. The application would be used in a similar way to other social media apps, albeit on a smaller scale.

### User Value

User stories with relevant acceptance criteria have been created to demonstrate the value that users would derive from using this app. These user stories are listed below:

### #1 Paginated Post Feed (must-have)

As a user, I want to see a feed of posts so I can browse recent updates from others.

**Acceptance Criteria**

- Posts are displayed in reverse chronological order.
- Only a limited number of posts are shown per page.
- Pagination controls allow navigation between pages.

### #2 Create Posts and Comments (must-have)

As a user, I want to share posts and comment on other users' posts so I can interact with my community.

**Acceptance Criteria**

- Logged-in users can create posts and comments.
- Comments are attached to the relevant post.

### #3 Edit and Delete Posts (should-have)

As a user, I want to be able to edit/delete my posts so I can make changes if I've made a mistake or want to remove something I've posted.

**Acceptance Criteria**

- Users can edit their own posts.
- Users can delete their own posts.

### #4 Events Section (must-have)

**User Story**

As a user, I want to know what's going on in my community so I can get involved in events.

**Acceptance Criteria**

- Events are listed in a separate section of the site.
- All important details are included, such as name, date, location.

### #5 RSVP to Events (must-have)

**User Story**

As a user, I want to indicate that I am interested in an event so that I can join it.

**Acceptance Criteria**

- Events have an option to RSVP.
- Users are notified of their RSVP status.

### #6 Marketplace Section (must-have)

**User Story**

As a user, I want to be able to see local listings of items for sale so I can look for good buying opportunities.

**Acceptance Criteria**

- Sale listings are featured in a separate Marketplace section of the site.
- Sale listings contain all information about the sale, including name, description, price.

### #7 Add Marketplace Listings and Auctions (must-have)

**User Story**

As a user, I want to be able to add listings and start auctions so I can make a little extra money from stuff I no longer need.

**Acceptance Criteria**

- Users can create sale listings that other users can interact with.
- Users can create auctions that other users can interact with.

### #8 Save Marketplace Listings (could-have)

**User Story**

As a user, I want to be able to save sale listings for later so I can manage my Marketplace activity.

**Acceptance Criteria**

- Users can add sales listings to a Wanted section.
- Users can delete sales listings in their Wanted section.

### #9 Registration and Login (must-have)

**User Story**

As a new user, I want to register and log in so I can access and contribute to the platform.

**Acceptance Criteria**

- Registration form includes username and password.
- Login form accepts valid credentials.
- Users can logout.

### #10 Password Reset (should-have)

**User Story**

As a user, I want to be able easily reset my password so that I can ensure account safety .

**Acceptance Criteria**

- Account section has functionality to change password.
- Changing password will require correct answers to security questions.

### #11 Site Navigation (must-have)

**User Story**

As a user, I want to be able to navigate around the site easily so that I can have a smooth user experience.

**Acceptance Criteria**

- Navigation to different sections of the website, including the User section, is intuitive and easy.
- Navigation icons are highlighted when active to indicate current location on the site.

### #12 Calm and Consistent Design (should-have)

**User Story**

As a user, I want the website to have a calm and consistent design so I can have an excellent user experience.

**Acceptance Criteria**

- An appropriate colour scheme is chosen for the overall site design.
- Colours are calm and minimalistic, with no contrast issues.
- The design is consistent throughout the website.

- - -

In addition, a dedicated GitHub project board has been created and used to drive development and manage project tasks. This project board is linked below:

[GitHub Project Board](https://github.com/users/arun-dhanjal/projects/9)

- - -

## Design

### Colour Scheme

![Our Corner Colour Palette](/readme-docs/our-corner-palette.png)

A palette of differing shades of orange and pastel yellow was chosen for the theme of this application. The intention was to keep things looking relatively minimalistic with splashes of a key colour throughout. The majority of buttons use these shades of orange with grey text. Edit and delete icons are grey whilst inactive, turning light orange on hover, fitting the minimalistic style. Navigation icons are coloured grey, but also turn orange on hover or when active.

One key exception to the overarching colour scheme applies to content that is pending approval. Posts and comments that are yet to be approved will be highlighted in a pale, muted yellow with an orange dotted border around the card. This combination has been chosen to make it clear when content is pending approval whilst remaining easy on the eye.

The colour palette was created using the [Coolors](https://coolors.co/) website.

### Typography

Although other fonts could have been implemented, the default fonts work very well with the design of the site and so no other fonts have been selected. However, other fonts could be used in future iterations, in which case Google Fonts will be utilised for this purpose.

### Page Layout

Wireframes were created based on the initial page layout designs for various screen sizes. The final deployed application has some minor stylistic changes/additions, and the layout of content differs between the main sections, but for the most part follows the same general design. Wireframes shown below:

#### Wireframe Mobile
![Wireframe Mobile](/readme-docs/wireframe-mobile.png)
#### Wireframe Tablet
![Wireframe Tablet](/readme-docs/wireframe-tablet.png)
#### Wireframe Desktop
![Wireframe Desktop](/readme-docs/wireframe-desktop.png)

### Database Structure

The back-end databases were designed at the start of the project with the intention of remaining unchanged throughout the development in order to avoid later complications. The Entity Relationship Diagram (ERD) can be viewed below:

***ERD STILL PENDING - EXAMPLE BELOW***

![< ERD >](/readme-docs/erd.png)

### Features

***[Arun's section]***
#### Site header

  ![< Site header >](/readme-docs/feature-site-header.png)

  * Site header contains site logo, site title, and User icon for authentication options

  * Site logo and header serve as navigation links to Feed page (essentially the home page)

  * User icon redirects to Login page if logged out; has a dropdown menu with Profile, Change Password, and Logout if logged in

  * Site header sticks to the top of the window on every page in the site

#### Site footer

  ![ Site footer ](/readme-docs/feature-site-footer.png)

  * Site footer that features at the bottom of every page in the site

  * Contains minimal information about the application

  * Retains same colour scheme as the site header for thematic consistency

***[Mortaza's section]***

***[Adam's section]***

***[Ysabela's section]***

***[Rich's section]***



#### Future implementations:

Although all must-have, should-have, and could-have user stories were fulfilled for this project, additional features could add value to this site. Some examples of which are:

  * User profile section: an area for users to manage their content in one place and manage their username and password

  * Profile images on submitted content: a small profile icon would be useful to include next to posts, comments, events, and marketplace listings to give each user more of an identity in the community

  * Comment count on posts: it would be useful to have an indication of how many comments are on a post before viewing the detail page

  * Likes/reactions on content: more interaction between users could be facilitated by adding options to add likes or reactions to posts and comments

### Accessibility

Mindful development has been exercised throughout the project to ensure the application is as accessible and user-friendly as possible. This includes:

* Using semantic HTML.

* Ensuring that there is a sufficient colour contrast throughout the site.

* Ensuring that navigation is intuitive and easy.

* Ensuring interactive elements and inputs are easy to recognise and use.

* Including appropriate aria labelling and alt tags.

- - -

## Technologies Used

### Languages Used

Python (Django) - For backend logic, models, views, and routing.

HTML & CSS - For structure and styling.

JavaScript - For some front-end user interaction and logic.

Django Template Language (DTL) - For dynamic rendering and template logic.

### Frameworks, Libraries & Programs Used

Git - For version control.

GitHub - To save and store the files for the app, as well as for project management.

Django version 4.2 - Used as the full stack framework to connect the front and back end using MVT (model-view-template) methodology.

PostgreSQL - The chosen RDBMS for this project.

Bootstrap version 5.3 - To utilise a number of Bootstrap components, including cards, buttons, and classes for styling. Additional CSS styling was also implemented in style.css.

Django crispy forms - Used for responsive form rendering with Bootstrap 5.

Browser Dev Tools - To troubleshoot and test features, solve issues with responsiveness, and styling.

Microsoft PowerPoint - To manually create the initial wireframes and site title.

Microsoft Excel - To create the database structure ERD tables, and to track and manage code checking and testing exercises.

Microsoft Copilot - For code queries, troubleshooting Django views and templates, refining logic, and converting Excel tables into Markdown format.

OpenAI ChatGPT - For code queries and resolution of coding issues.

[Heroku](https://www.heroku.com/) - To host the web application via Eco Dynos. This has been chosen as it allows for full-stack web applications to be hosted, as opposed to GitHub which only allows for front-end applications.

[Cloudinary](https://cloudinary.com/) - To host user-uploaded images via a cloud-based server; this is necessary given Heroku's ephemeral file system on Eco Dynos.

[favicon.io](https://favicon.io/) - To convert the site logo into a favicon-sized image.

[DBeaver](https://dbeaver.com/) - To create the ERD document.

[TechSini](https://techsini.com/multi-mockup/) - To show the site image on a range of devices.

- - -

## Deployment

Heroku was used to deploy the live application. The instructions to achieve this are below:

1. Log in to Heroku and navigate to your dashboard.
2. Create a new app with a unique name.
3. Go back to your workspace and install a production-ready webserver for Heroku, e.g. Gunicorn.
4. Add the webserver to your requirements.txt file.
5. Create a Procfile in your root directory and declare the Gunicorn web process.
6. Add the '.herokuapp.com' hostname to the list of ALLOWED_HOSTS.
7. Add, commit, and push your changes to GitHub.
8. Move back to Heroku and click the Deploy tab.
9. In Deployment method, choose Connect to GitHub and select your GitHub repo.
10. Scroll to the bottom of the page and click Deploy Branch to start a manual deployment.

- - -

## Testing

### Manual Functionality Testing

***MANUAL FUNCTIONALITY TESTING PENDING - EXAMPLE BELOW***

Manual testing was carried out to ensure functionality of all processes was as expected. The results of these tests are below:

| **Site Area**         | **User Action**                                                                                      | **Expected Result**                                                                                                                       | **Pass/Fail** |
|-----------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| Header                | Click site logo/title                                                                                | Redirect to Feed page                                                                                                                     | Pass         |
| Header                | Click Sign Up button                                                                                 | Redirect to Sign Up page                                                                                                                  | Pass         |
| Sign Up page          | Fill out Sign Up form correctly and click Submit                                                     | Redirect to Feed page as new logged-in user, displaying feedback message at top of page                                                  | Pass         |
| Sign Up page          | Fill out Sign Up form incorrectly and click Submit                                                   | Validation error displays with instructions to amend                                                                                      | Pass         |
| Header                | Click Log In button                                                                                  | Redirect to Log In page                                                                                                                   | Pass         |
| Log In page           | Fill out Log In form correctly and click Submit                                                      | Redirect to Feed page as logged-in user, displaying feedback message at top of page                                                      | Pass         |
| Log In page           | Fill out Log In form incorrectly and click Submit                                                    | Validation error displays with instructions to amend                                                                                      | Pass         |
| Header                | Click Log Out button                                                                                 | Redirect to Log Out page                                                                                                                  | Pass         |
| Log Out page          | Click Log Out button                                                                                 | Redirect to Feed page as logged-out user, displaying feedback message at top of page                                                     | Pass         |
| Nav icons             | Click Home icon                                                                                      | Redirect to Feed page                                                                                                                     | Pass         |
| Nav icons             | Click Reviews icon                                                                                   | Redirect to Puzzle List page                                                                                                              | Pass         |
| Nav icons             | Click Leaderboards icon                                                                              | Redirect to Leaderboards page                                                                                                             | Pass         |
| Feed page             | Click Sign Up button                                                                                 | Redirect to Sign Up page                                                                                                                  | Pass         |
| Feed page             | Click New Post button                                                                                | Redirect to Create a Post page                                                                                                            | Pass         |
| Create a Post page    | Fill out Create a Post form and click Submit                                                         | Redirect to Feed page with new unapproved post at top of feed, displaying feedback message at top of page                                | Pass         |
| Feed page             | Click Edit button on user-owned post                                                                 | Redirect to Edit Post page                                                                                                                | Pass         |
| Edit Post page        | Update Post form and click Save                                                                      | Redirect to Post Detail page for that post displaying updated and now unapproved post, also displaying feedback message at top of page   | Pass         |
| Feed page             | Click Delete button on user-owned post                                                               | Display Delete Post modal                                                                                                                 | Pass         |
| Delete Post modal     | Click X button                                                                                       | Closes modal                                                                                                                              | Pass         |
| Delete Post modal     | Click Cancel button                                                                                  | Closes modal                                                                                                                              | Pass         |
| Delete Post modal     | Click Delete button                                                                                  | Deletes post and redirects to Feed page, displaying feedback message at top of page                                                      | Pass         |
| Feed page             | Click View Post button on a post                                                                     | Redirect to Post Detail page of that post                                                                                                 | Pass         |
| Feed page             | Click Previous pagination button                                                                     | Go to previous page of feed                                                                                                               | Pass         |
| Feed page             | Click Next pagination button                                                                         | Go to next page of feed                                                                                                                   | Pass         |
| Post Detail page      | Click Edit button on user-owned post                                                                 | Redirect to Edit Post page                                                                                                                | Pass         |
| Edit Post page        | Update Post form and click Save                                                                      | Redirect to Post Detail page for that post displaying updated and now unapproved post, also displaying feedback message at top of page   | Pass         |
| Post Detail page      | Click Delete button on user-owned post                                                               | Display Delete Post modal                                                                                                                 | Pass         |
| Delete Post modal     | Click X button                                                                                       | Closes modal                                                                                                                              | Pass         |
| Delete Post modal     | Click Cancel button                                                                                  | Closes modal                                                                                                                              | Pass         |
| Delete Post modal     | Click Delete button                                                                                  | Deletes post and redirects to Feed page, displaying feedback message at top of page                                                      | Pass         |
| Post Detail page      | Fill out Comment form and click Submit                                                               | New unapproved comment shows in comment list, and feedback message displays at top of page                                               | Pass         |
| Post Detail page      | Click Edit button on user-owned comment                                                              | Redirect to Edit Comment page                                                                                                             | Pass         |
| Edit Comment page     | Update Comment form and click Save                                                                   | Redirect to Post Detail page of related post, displaying updated and now unapproved comment, also displaying feedback message at top of page     | Pass         |
| Post Detail page      | Click Delete button on user-owned comment                                                            | Display Delete Comment modal                                                                                                              | Pass         |
| Delete Comment modal  | Click X button                                                                                       | Closes modal                                                                                                                              | Pass         |
| Delete Comment modal  | Click Cancel button                                                                                  | Closes modal                                                                                                                              | Pass         |
| Delete Comment modal  | Click Delete button                                                                                  | Deletes comment and redirects to related post's Post Detail page, displaying feedback message at top of page                             | Pass         |
| Puzzle List page      | Click See Reviews button on a puzzle                                                                 | Redirects to Puzzle Detail page                                                                                                           | Pass         |
| Puzzle List page      | Click Previous pagination button                                                                     | Go to previous page of Puzzle List                                                                                                        | Pass         |
| Puzzle List page      | Click Next pagination button                                                                         | Go to next page of Puzzle List                                                                                                            | Pass         |
| Puzzle Detail page    | Fill out Review form and click Submit                                                                | New unapproved review shows in review list, displaying feedback message at top of page                                                   | Pass         |
| Puzzle Detail page    | Click Edit button on user-owned review                                                               | Redirect to Edit Review page                                                                                                              | Pass         |
| Edit Review page      | Update Review form and click Submit                                                                  | Redirect to Puzzle Detail page of related puzzle, displaying updated and now unapproved review, and displaying feedback message at top of page   | Pass         |
| Puzzle Detail page    | Click Delete button on user-owned review                                                             | Display Delete Review modal                                                                                                               | Pass         |
| Puzzle Detail page    | Click X button                                                                                       | Closes modal                                                                                                                              | Pass         |
| Puzzle Detail page    | Click Cancel button                                                                                  | Closes modal                                                                                                                              | Pass         |
| Puzzle Detail page    | Click Delete button                                                                                  | Deletes review and redirects to related puzzle's Puzzle Detail page, displaying feedback message at top of page                          | Pass         |
| Leaderboards page     | Click Sign Up button                                                                                 | Redirects to Sign Up page                                                                                                                 | Pass         |
| Leaderboards page     | Click Submit Time button                                                                             | Redirects to Submit Time page                                                                                                             | Pass         |
| Submit Time page      | Fill out Submit Time form correctly and click submit                                                 | Redirect to Leaderboards page with submitted time now showing in relevant puzzle's leaderboard                                           | Pass         |
| Submit Time page      | Fill out Submit Time form incorrectly and click submit                                               | Validation error displays with instructions to amend                                                                                      | Pass         |
| Submit Time page      | Fill out Submit Time form for puzzle that already has your time                                      | Error message displays advising that only one time can be submitted per puzzle                                                           | Pass         |
| Leaderboards page     | Click Update Time button                                                                             | Redirect to Update Time page                                                                                                              | Pass         |
| Update Time page      | Fill out Update Time form correctly and click submit                                                 | Redirect to Leaderboards page with updated time now showing in relevant puzzle's leaderboard                                             | Pass         |
| Update Time page      | Fill out Update Time form incorrectly and click submit                                               | Validation error displays with instructions to amend                                                                                      | Pass         |

### Device Responsivity Testing

***DEVICE RESPONSIVITY TESTING PENDING - EXAMPLE TEXT BELOW***

Responsivity tests were carried out to ensure that the application displayed correctly on a number of different device sizes. For completeness, all of the default device sizes in Google Chrome's Developer Tools were tested for responsiveness by emulating each device and then navigating through the site to note any layout or formatting issues. Almost all devices returned zero issues with two exceptions, detailed below:

- Microsoft Lumia 550: Dev Tools defaults to a landscape view for this device, which makes the viewport height very short, leading to a sub-optimal user experience. However, the application is not intended to be used in landscape mode on mobile devices, and in fact the default landscape view for this device in Dev Tools is a known error, with the expected view being portrait as is the case with most mobile devices. As such, this case is of no concern for this application.

- JioPhone 2: The viewport for this device is very small at just 240 x 320 px (it is defined as a "compact device") which causes issues with layout. However, this application is not intended to be used on such small devices, and so is of no concern for this application.

## Validation

Various validation software were used to validate and/or lint the code in each of the files written for this project. Most errors or bugs were identified and fixed, however some remain and will need to fixed in a further iteration of this project. Screenshots evidencing validation process below:

### [W3C Validator: HTML](https://validator.w3.org/)

***[Arun's section]***

***[Mortaza's section]***

***[Adam's section]***

***[Ysabela's section]***




***[Rich's section]***

#### Marketplace HTML Validation

![HTML validation Marketplace screenshot](/readme-docs/marketplace-stuff/html-validation-marketplace.png)

#### Marketplace Python Linter Validation

marketplace/admin.py
![Python linter marketplace/admin.py screenshot](/readme-docs/marketplace-stuff/python-linter-marketplace-admin.png)

marketplace/models.py
![Python linter marketplace/models.py screenshot](/readme-docs/marketplace-stuff/python-linter-marketplace-models.png)

marketplace/urls.py
![Python linter marketplace/urls.py screenshot](/readme-docs/marketplace-stuff/python-linter-marketplace-urls.png)

marketplace/views.py
![Python linter marketplace/views.py screenshot](/readme-docs/marketplace-stuff/python-linter-marketplace-views.png)

ERD Diagram Link => [View Full ERD Diagram](/readme-docs/marketplace-stuff/social-ERD.png)




### [W3C Validator: CSS](https://jigsaw.w3.org/css-validator/)

style.css
![CSS validation screenshot](/readme-docs/css-validation.png)

marketplace.css
![CSS validation screenshot](/readme-docs/css-marketplace-validation.png)

### [CI Python Linter: Python](https://pep8ci.herokuapp.com/)

***[Mortaza's section]***

user/admin.py

![Python linter user/admin.py screenshot](/readme-docs/python-linter-user-admin.png)

user/apps.py

![Python linter user/apps.py screenshot](/readme-docs/python-linter-user-apps.png)

user/forms.py

![Python linter user/forms.py screenshot](/readme-docs/python-linter-user-forms.png)

user/models.py

![Python linter user/admin.py screenshot](/readme-docs/python-linter-user-models.png)

user/signals.py

![Python linter user/signals.py screenshot](/readme-docs/python-linter-user-signals.png)

user/tests.py

![Python linter user/tests.py screenshot](/readme-docs/python-linter-user-tests.png)

user/urls.py

![Python linter user/urls.py screenshot](/readme-docs/python-linter-user-urls.png)

user/views.py

![Python linter user/views.py screenshot](/readme-docs/python-linter-user-views.png)

***[Adam's section]***

***[Ysabela's section]***

***[Rich's section]***

### [WAVE: Web Accessibility Evaluation Tool](https://wave.webaim.org/)

![WAVE validation](/readme-docs/wave.png)

***[Arun's section]***

### Lighthouse: Mobile

![Lighthouse mobile validation screenshot](/readme-docs/lighthouse-mobile.png)

***[Arun's section]***

### Lighthouse: Desktop

![Lighthouse desktop validation screenshot](/readme-docs/lighthouse-desktop.png)

***[Arun's section]***

- - -

## AI Usage
AI has been used extensively throughout this project, with the main assistant of choice being Microsoft Copilot, however OpenAI's ChatGPT has also been used on occassion. Listed below are the ways AI has specifically been used during this project:

* Troubleshooting Django logic in Python files

* Refining template logic in HTML files

* Creation of the site logo

* Converting Excel files into markdown format (e.g. for the markdown table featured in the Testing section of this README)

* Scanning code files for formatting and PEP8 issues to expedite the code-tidying process

* General sounding board (e.g. asking if certain implementations or functionalities would be a good idea before committing to them)

Please note: although AI has been utilised during the development of this app, any and all AI outputs have been scrutinised and considered carefully before being implemented. The developers appreciate that AI is a tool to be used and not relied on without complete understanding of the output.

## Credits
### Content

Some site content has been produced manually, such as:

- Site title: created manually in PowerPoint
- Posts, comments, events, marketplace items: created manually by the team of developers

Some site content has been produced with the help of AI, such as:

- Site logo

### Contributors

This app is the result of collaboration between a team of contributors, including:

* Mortaza Zolfpour - https://github.com/arokhlo
* Adam Haines - https://github.com/ETCocoa
* Ysabela Bathan - https://github.com/KoroYsabela
* Arun Dhanjal - https://github.com/arun-dhanjal
* Richard Vandenbergh - https://github.com/Richardv10
