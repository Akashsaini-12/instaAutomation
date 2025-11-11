# 🛡️ Instagram Automation Safety Guidelines

## ⚠️ IMPORTANT: Account Protection

This automation tool implements **comprehensive safety measures** to protect your Instagram account from bans. However, **no automation is 100% safe**. Please read and follow these guidelines carefully.

## 🔒 Built-in Safety Features

### 1. Rate Limiting
- **Posts**: Maximum 10 per day, 2 per hour (default)
- **Comments**: Maximum 20 per hour
- **Likes**: Maximum 50 per hour
- **Replies**: Maximum 5 per post, 20 per hour

### 2. Randomized Delays
- **Between Posts**: 10-30 minutes (randomized)
- **Between Likes**: 3-5 seconds (randomized)
- **Between Replies**: 20-30 seconds (randomized)
- **Human-like Behavior**: All delays include random variations

### 3. Action Tracking
- All actions are tracked and logged
- Daily and hourly limits are enforced
- Automatic blocking when limits are reached

### 4. Error Handling
- Exponential backoff on rate limit errors
- Automatic detection of Instagram rate limits
- Graceful handling of account warnings

## 📋 Recommended Settings

### Safe Settings (Default)
```env
# Posting - Very Safe
POST_DELAY_SECONDS=900          # 15 minutes between posts
POST_DELAY_RANDOM_MIN=600       # 10 minutes minimum
POST_DELAY_RANDOM_MAX=1800      # 30 minutes maximum

# Daily/Hourly Limits - Conservative
MAX_POSTS_PER_DAY=10            # Maximum 10 posts per day
MAX_POSTS_PER_HOUR=2            # Maximum 2 posts per hour
MAX_COMMENTS_PER_HOUR=20        # Maximum 20 comments per hour
MAX_LIKES_PER_HOUR=50           # Maximum 50 likes per hour

# Auto-interactions - Limited
AUTO_LIKE_MAX_PER_POST=10       # Max 10 likes per post
AUTO_LIKE_DELAY_BETWEEN=5       # 5 seconds between likes
AUTO_REPLY_MAX_PER_POST=5       # Max 5 replies per post
AUTO_REPLY_DELAY_BETWEEN=30     # 30 seconds between replies
```

### Ultra-Safe Settings (For New Accounts)
```env
# Posting - Ultra Conservative
POST_DELAY_SECONDS=1800         # 30 minutes between posts
POST_DELAY_RANDOM_MIN=1200      # 20 minutes minimum
POST_DELAY_RANDOM_MAX=3600      # 60 minutes maximum

# Daily/Hourly Limits - Very Conservative
MAX_POSTS_PER_DAY=5             # Maximum 5 posts per day
MAX_POSTS_PER_HOUR=1            # Maximum 1 post per hour
MAX_COMMENTS_PER_HOUR=10        # Maximum 10 comments per hour
MAX_LIKES_PER_HOUR=30           # Maximum 30 likes per hour
```

## ⚡ Instagram Guidelines Compliance

### ✅ DO:
1. **Use realistic delays** - Never post more than 1-2 posts per hour
2. **Vary your posting times** - Don't post at the same time every day
3. **Limit interactions** - Don't like/comment on too many posts at once
4. **Monitor your account** - Check for warnings or restrictions
5. **Use session management** - Let the tool save your session
6. **Respect rate limits** - When blocked, wait before retrying

### ❌ DON'T:
1. **Don't exceed limits** - Never override safety limits
2. **Don't automate 24/7** - Give your account breaks
3. **Don't spam** - Don't post the same content repeatedly
4. **Don't ignore warnings** - If Instagram warns you, stop automation
5. **Don't use multiple accounts** - Don't automate from the same IP
6. **Don't bypass rate limits** - This will get your account banned

## 🚨 Warning Signs

If you see any of these, **STOP AUTOMATION IMMEDIATELY**:

1. **Account Warnings**: "Your account has been restricted"
2. **Rate Limit Errors**: "Please wait a few minutes"
3. **Login Issues**: Repeated login failures
4. **Action Blocks**: "Action blocked. Try again later"
5. **Shadow Banning**: Your posts aren't showing up

## 🛠️ What to Do If You Get Rate Limited

1. **Stop automation immediately**
2. **Wait 24-48 hours** before resuming
3. **Reduce your limits** in the config
4. **Increase delays** between actions
5. **Use the account manually** for a few days

## 📊 Monitoring Your Account

The safety manager tracks all actions and provides statistics:

- **Daily Action Counts**: How many actions today
- **Hourly Action Counts**: How many actions in the last hour
- **Rate Limit Events**: When rate limits were hit

Check the logs regularly to monitor your account's activity.

## 🔧 Configuration

All safety settings can be configured in your `.env` file:

```env
# Rate Limiting
MAX_POSTS_PER_DAY=10
MAX_POSTS_PER_HOUR=2
MAX_COMMENTS_PER_HOUR=20
MAX_LIKES_PER_HOUR=50

# Delays
POST_DELAY_SECONDS=900
POST_DELAY_RANDOM_MIN=600
POST_DELAY_RANDOM_MAX=1800

# Auto-interactions
AUTO_LIKE_MAX_PER_POST=10
AUTO_LIKE_DELAY_BETWEEN=5
AUTO_REPLY_MAX_PER_POST=5
AUTO_REPLY_DELAY_BETWEEN=30

# Error Handling
ENABLE_EXPONENTIAL_BACKOFF=true
MAX_RETRY_ATTEMPTS=3
RETRY_BASE_DELAY=60
```

## 📝 Best Practices

1. **Start Slow**: Begin with conservative limits and increase gradually
2. **Monitor Closely**: Check your account and logs regularly
3. **Use Manually**: Don't automate 100% - use your account manually too
4. **Vary Content**: Don't post the same type of content repeatedly
5. **Respect Limits**: Never exceed the recommended limits
6. **Take Breaks**: Give your account days off from automation

## ⚖️ Legal Notice

**This tool is for educational purposes only.**
- Instagram's Terms of Service prohibit automation
- Use at your own risk
- The authors are not responsible for account bans
- Always follow Instagram's Community Guidelines

## 🆘 Support

If you experience issues:
1. Check the logs for error messages
2. Review your configuration settings
3. Reduce your limits and delays
4. Wait before retrying after errors

## 📚 Additional Resources

- [Instagram Terms of Service](https://help.instagram.com/581066165581870)
- [Instagram Community Guidelines](https://help.instagram.com/477434105621119)
- [Instagram Rate Limits](https://developers.facebook.com/docs/instagram-api/overview)

---

**Remember**: Your account safety is your responsibility. Use automation wisely and always prioritize your account's health over automation speed.

