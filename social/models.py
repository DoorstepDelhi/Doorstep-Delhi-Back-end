from django.db import models


class Follower(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="followers")
    follower = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="following")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "follower")


class Post(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class PostImage(models.Model):
    post = models.ForeignKey('social.Post', on_delete = models.CASCADE )
    image = models.ImageField()


class PostFile(models.Model):
    post = models.ForeignKey('social.Post', on_delete = models.CASCADE )
    file = models.FileField()
    video = models.BooleanField(default = False)


Post_React_Choices = (
    ("Like", "Like"),
    ("Celebrate", "Celebrate"),
)


class PostReact(models.Model):
    post = models.ForeignKey('social.Post', on_delete = models.CASCADE )
    user = models.ForeignKey('accounts.User', on_delete = models.CASCADE )
    type = models.CharField(max_length = 10, choices = Post_React_Choices )
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Post Reacts"
        unique_together = ['post', 'user']


class PostComment(models.Model):
    post = models.ForeignKey('social.Post', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    comment = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)


class PostCommentReply(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE,related_name="user_reply")
    comment = models.ForeignKey('social.PostComment', on_delete = models.CASCADE)
    reply = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Post Comment Replies"


class PostShare(models.Model):
    post = models.ForeignKey('social.Post', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add = True)
