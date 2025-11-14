### Features

#### Main feed page

![Main feed page](readme-docs/feed/feature-main-page.png)

- The Feed page is the "main" page of the site. It functions as a blog, with users being able to create posts and comment on them.
- The navigation and search functions are site-wide.

#### Example post in feed

![Example post in feed](readme-docs/feed/feature-example-post.png)

- This is how a post is shown in the feed list. The post's title, author, creation date, text content, and opionally an image are shown.
- The user can click the Read Me button to visit the post's page, where they can add a comment.

#### Signup required to post message

![Signup required to post message](readme-docs/feed/feature-signup-to-post.png)

- If a user isn't logged in, then instead of a section allowing them to create a post, a Sign Up button is shown instead. 

#### New post form

![New post form](readme-docs/feed/feature-new-post.png)

- When logged in, the user is allowed to add a post to the feed.
- The post can optionally include an image.
- The user must add a title and some text in the content field.
- The post must be accepted by an admin or superuser before other site users can see it. This moderation is to prevent harassmnent or illegal content from being posted on the site.

#### Post created notification

![Post created notification](readme-docs/feed/feature-post-created.png)

- After a post is created, a notification will pop up informing the user.

#### Post awaiting approval

![Post awaiting approval modal](readme-docs/feed/feature-post-awaiting-approval.png)

- After a user creates a post, it will need to be approved by an admin/superuser before it is visible to all site users.
- The user who created the post can still see it, though it is marked as "awaiting approval" with a different background colour.

#### Edit and delete options on a post

![Edit and delete options on a post](readme-docs/feed/feature-edit-and-delete.png)

- On their own posts, the user has an edit and a delete button.

#### Edit post form

![Edit post form](readme-docs/feed/feature-edit-post.png)

- A site user can edit one of their own already-existing posts. They can add/remove an image, change the title, and change the text content.
- Once saved, the edit must be approved by an admin/superuser before it can take effect.

#### Edit notification message

![Edit notification message](readme-docs/feed/feature-edit-notification.png)

- After the user saves an edited post, they get a notification informing them it was a success and that it is now pending approval.

#### Delete confirmation modal

![Delete confirmation modal](readme-docs/feed/feature-delete-confirmation-modal.png)

- When a user clicks the delete button on one of their posts, a modal pops up, asking for confirmation if they want to actually delete the post. This is to prevent accidental deletions.
- If they click cancel, the modal goes away and nothing happens. If they click delete, then the post will finally be deleted.

#### Delete notification message

![Delete notification message](readme-docs/feed/feature-delete-notificaiton.png)

- After a user deletes one of their own posts, they get a notification telling them it has been successfully deleted.

#### Example comments under a post

![Example comments under a post](readme-docs/feed/feature-example-comments.png)

- Comments go under a specific post. They show the author, creation date, and text content.
- If the user isn't logged in, then they cannot yet comment. Instead, a button asking them to Sign Up is shown.

#### New comment input

![New comment input](readme-docs/feed/feature-new-comment.png)

- When logged in, the user is allowed to add a comment to a post.
- The comment must be accepted by an admin or superuser before other site users can see it. This moderation is to prevent harassmnent or illegal content from being posted on the site.

#### Comment awaiting approval

![Comment awaiting approval modal](readme-docs/feed/feature-comment-awaiting-approval.png)

- After a user creates a comment, it goes into awaiting approval status. Only the user themselves can see this comment. It will only be shown to all site users once an admin/superuser approves it.

### Python Linter

#### feed/admin.py

![Python linter results for feed/admin.py](readme-docs/feed/python-linter-feed-admin.png)

#### feed/apps.py

![Python linter results for feed/apps.py](readme-docs/feed/python-linter-feed-apps.png)

#### feed/forms.py

![Python linter results for feed/forms.py](readme-docs/feed/python-linter-feed-forms.png)

#### feed/models.py

![Python linter results for feed/models.py](readme-docs/feed/python-linter-feed-models.png)

#### feed/search.py

![Python linter results for feed/search.py](readme-docs/feed/python-linter-feed-search.png)

#### feed/tests.py

![Python linter results for feed/tests.py](readme-docs/feed/python-linter-feed-tests.png)

#### feed/urls.py

![Python linter results for feed/urls.py](readme-docs/feed/python-linter-feed-urls.png)

#### feed/views.py

![Python linter results for feed/views.py](readme-docs/feed/python-linter-feed-views.png)

### HTML Validation

#### Main Feed Page

![HTML validation results for main feed page](readme-docs/feed/html-validation-feed-page.png)

#### Feed Post Detail

![HTML validation results for feed post detail page](readme-docs/feed/html-validation-feed-post-detail.png)

#### Feed Edit Post

![HTML validation results for feed edit post page](readme-docs/feed/html-validation-feed-edit-post.png)

#### Feed Search

![HTML validation results for feed search page](readme-docs/feed/html-validation-feed-search.png)
