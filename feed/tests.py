from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment
from .forms import PostForm, CommentForm


# ===== MODEL TESTS =====

class PostModelTest(TestCase):
    """Test the Post model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='This is test content',
            author=self.user,
            accepted=True
        )
    
    def test_post_creation(self):
        """Test creating a post"""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is test content')
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(self.post.accepted)
        
    def test_post_string_representation(self):
        """Test __str__ method"""
        expected = f"{self.post.title} - {self.user.username}"
        self.assertEqual(str(self.post), expected)
        
    def test_post_ordering(self):
        """Test that posts are ordered by created_on descending"""
        post2 = Post.objects.create(
            title='Second Post',
            content='Content',
            author=self.user,
            accepted=True
        )
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], post2)  # Newer post first
        self.assertEqual(posts[1], self.post)
        
    def test_post_default_accepted_is_false(self):
        """Test that posts are not accepted by default"""
        post = Post.objects.create(
            title='Unaccepted Post',
            content='Content',
            author=self.user
        )
        self.assertFalse(post.accepted)


class CommentModelTest(TestCase):
    """Test the Comment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            author=self.user,
            accepted=True
        )
        
    def test_comment_creation(self):
        """Test creating a comment"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment',
            accepted=True
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, 'Test comment')
        self.assertTrue(comment.accepted)
        
    def test_comment_string_representation(self):
        """Test __str__ method"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        expected = f"{self.user.username} commented on: {self.post} by {self.user.username}"
        self.assertEqual(str(comment), expected)
        
    def test_comment_ordering(self):
        """Test that comments are ordered by created_on ascending"""
        comment1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='First comment'
        )
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Second comment'
        )
        comments = list(Comment.objects.all())
        self.assertEqual(comments[0], comment1)  # Older comment first
        self.assertEqual(comments[1], comment2)
        
    def test_comment_cascade_deletion(self):
        """Test that comments are deleted when post is deleted"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.post.delete()
        self.assertEqual(Comment.objects.count(), 0)


# ===== VIEW TESTS =====

class FeedViewTest(TestCase):
    """Test the Feed view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_feed_view_loads(self):
        """Test that feed page loads successfully"""
        response = self.client.get(reverse('feed:feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/feed.html')
        
    def test_feed_shows_accepted_posts(self):
        """Test that accepted posts appear in feed"""
        post = Post.objects.create(
            title='Accepted Post',
            content='Content',
            author=self.user,
            accepted=True
        )
        response = self.client.get(reverse('feed:feed'))
        self.assertContains(response, 'Accepted Post')
        
    def test_feed_hides_unaccepted_posts_for_anonymous(self):
        """Test that unauthenticated users don't see unaccepted posts"""
        post = Post.objects.create(
            title='Unaccepted Post',
            content='Content',
            author=self.user,
            accepted=False
        )
        response = self.client.get(reverse('feed:feed'))
        self.assertNotContains(response, 'Unaccepted Post')
        
    def test_feed_shows_own_unaccepted_posts_when_authenticated(self):
        """Test that users see their own unaccepted posts"""
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(
            title='My Unaccepted Post',
            content='Content',
            author=self.user,
            accepted=False
        )
        response = self.client.get(reverse('feed:feed'))
        self.assertContains(response, 'My Unaccepted Post')
        
    def test_create_post_authenticated(self):
        """Test creating a post when logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('feed:feed'), {
            'title': 'New Post',
            'content': 'New content'
        })
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'New Post')
        self.assertEqual(post.author, self.user)
        self.assertFalse(post.accepted)  # Should be pending approval


class PostDetailViewTest(TestCase):
    """Test the post detail view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            author=self.user,
            accepted=True
        )
        
    def test_post_detail_view_loads(self):
        """Test that post detail page loads"""
        response = self.client.get(reverse('feed:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/post_detail.html')
        self.assertContains(response, 'Test Post')
        
    def test_post_detail_shows_accepted_comments(self):
        """Test that accepted comments are displayed"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment',
            accepted=True
        )
        response = self.client.get(reverse('feed:post_detail', args=[self.post.id]))
        self.assertContains(response, 'Test comment')
        
    def test_create_comment_authenticated(self):
        """Test creating a comment when logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('feed:post_detail', args=[self.post.id]), {
            'content': 'New comment'
        })
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'New comment')
        self.assertEqual(comment.author, self.user)
        self.assertFalse(comment.accepted)  # Should be pending approval
        
    def test_unaccepted_post_not_accessible(self):
        """Test that unaccepted posts return 404"""
        unaccepted_post = Post.objects.create(
            title='Unaccepted',
            content='Content',
            author=self.user,
            accepted=False
        )
        response = self.client.get(reverse('feed:post_detail', args=[unaccepted_post.id]))
        self.assertEqual(response.status_code, 404)


# ===== FORM TESTS =====

class PostFormTest(TestCase):
    """Test the PostForm"""
    
    def test_valid_post_form(self):
        """Test valid form data"""
        form_data = {
            'title': 'Test Post',
            'content': 'Test content'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_empty_title_invalid(self):
        """Test that empty title is invalid"""
        form_data = {
            'title': '',
            'content': 'Test content'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_empty_content_invalid(self):
        """Test that empty content is invalid"""
        form_data = {
            'title': 'Test Post',
            'content': ''
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    """Test the CommentForm"""
    
    def test_valid_comment_form(self):
        """Test valid comment form data"""
        form_data = {
            'content': 'Test comment'
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_empty_content_invalid(self):
        """Test that empty content is invalid"""
        form_data = {
            'content': ''
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())


# ===== SEARCH TESTS =====

class SearchViewTest(TestCase):
    """Test the search functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_search_view_loads(self):
        """Test that search page loads"""
        response = self.client.get(reverse('feed:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/search_results.html')
        
    def test_search_finds_posts_by_title(self):
        """Test searching posts by title"""
        post = Post.objects.create(
            title='Kitten Photos',
            content='Content',
            author=self.user,
            accepted=True
        )
        response = self.client.get(reverse('feed:search'), {'q': 'kitten'})
        self.assertContains(response, 'Kitten Photos')
        
    def test_search_finds_posts_by_content(self):
        """Test searching posts by content"""
        post = Post.objects.create(
            title='My Post',
            content='This post is about kittens',
            author=self.user,
            accepted=True
        )
        response = self.client.get(reverse('feed:search'), {'q': 'kitten'})
        self.assertContains(response, 'My Post')
        
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        post = Post.objects.create(
            title='KITTEN',
            content='Content',
            author=self.user,
            accepted=True
        )
        response = self.client.get(reverse('feed:search'), {'q': 'kitten'})
        self.assertContains(response, 'KITTEN')
        
    def test_search_only_shows_accepted_posts(self):
        """Test that search only shows accepted posts"""
        accepted = Post.objects.create(
            title='Accepted Kitten',
            content='Content',
            author=self.user,
            accepted=True
        )
        unaccepted = Post.objects.create(
            title='Unaccepted Kitten',
            content='Content',
            author=self.user,
            accepted=False
        )
        response = self.client.get(reverse('feed:search'), {'q': 'kitten'})
        self.assertContains(response, 'Accepted Kitten')
        self.assertNotContains(response, 'Unaccepted Kitten')
        
    def test_empty_search_query(self):
        """Test search with empty query"""
        response = self.client.get(reverse('feed:search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0')  # Should show 0 results


# ===== PAGINATION TESTS =====

class FeedPaginationTest(TestCase):
    """Test feed pagination"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_pagination_with_many_posts(self):
        """Test that pagination works correctly"""
        # Create 10 posts (feed paginates by 6)
        for i in range(10):
            Post.objects.create(
                title=f'Post {i}',
                content='Content',
                author=self.user,
                accepted=True
            )
        
        # First page should have 6 posts
        response = self.client.get(reverse('feed:feed'))
        self.assertEqual(len(response.context['posts']), 6)
        
        # Second page should have 4 posts
        response = self.client.get(reverse('feed:feed') + '?page=2')
        self.assertEqual(len(response.context['posts']), 4)
