# 🏀🏈⚾🏒 Sports Standings Emailer

A GitHub Action that automatically fetches NBA, NFL, MLB, and NHL standings along with recent games and highlights, then sends comprehensive email updates to keep you informed about all major sports.

## Features

- **Multi-Sport Coverage**: NBA, NFL, MLB, and NHL standings
- **Recent Games**: Last 7 days of game results and scores
- **Game Highlights**: Key plays and important moments
- **Beautiful HTML Emails**: Formatted tables with team rankings, records, and statistics
- **Automated Scheduling**: Runs every Tuesday at 3 AM Pacific Time (11 AM UTC)
- **Manual Trigger**: Can be triggered manually via GitHub Actions
- **Error Handling**: Shows error messages instead of using fallback data

## Setup Instructions

### 1. Fork or Clone This Repository

First, fork this repository to your GitHub account or clone it locally.

### 2. Configure Email Settings

You'll need to set up email credentials. The easiest approach is using Gmail with an App Password:

#### Option A: Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Use these settings**:
   - SMTP Server: `smtp.gmail.com`
   - SMTP Port: `587`
   - Sender Email: Your Gmail address
   - Sender Password: The app password you generated

#### Option B: Other Email Providers

- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's SMTP settings

### 3. Set Up GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SENDER_EMAIL` | Your email address | `yourname@gmail.com` |
| `SENDER_PASSWORD` | Your email password/app password | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Your friend's email | `friend@gmail.com` |

### 4. Customize the Schedule

The default schedule runs every Tuesday at 3 AM Pacific Time (11 AM UTC). To change this:

1. Edit `.github/workflows/sports-standings.yml`
2. Modify the cron expression: `'0 11 * * 2'`

**Cron Schedule Examples:**
- `'0 11 * * 2'` - Every Tuesday at 11 AM UTC (3 AM PT)
- `'0 18 * * 2'` - Every Tuesday at 6 PM UTC (10 AM PT)  
- `'0 11 * * 1,4'` - Every Monday and Thursday at 11 AM UTC
- `'0 11 * * *'` - Every day at 11 AM UTC

### 5. Test the Setup

1. **Manual Test**: Go to Actions tab → Sports Update Email (Standings + Games) → Run workflow
2. **Check Logs**: Monitor the workflow execution for any errors
3. **Verify Email**: Check if your friend receives the email

## How It Works

### Data Sources
- **NBA**: ESPN API for real-time standings and recent games
- **NFL**: ESPN API for standings, scores, and highlights
- **MLB**: ESPN API for current standings and game results
- **NHL**: ESPN API for standings and recent matchups

### What's Included
- **Current Standings**: All teams ranked by conference/division
- **Recent Games**: Last 7 days of results with scores
- **Game Highlights**: Key plays and important moments
- **Team Records**: Wins, losses, win percentages, and games back

### Email Format
- Beautiful HTML formatting with organized tables
- Organized by conference/division for each sport
- Includes timestamp and friendly message
- Responsive design that works on mobile and desktop

## Customization Options

### Adding More Sports
To add other sports:

1. Add new API endpoints in `sports_emailer.py`
2. Create corresponding `get_*_standings()` methods
3. Add formatting methods for the new sport
4. Update the email template to include the new data

### Recent Games
The system automatically fetches recent game results:

1. Last 7 days of games for all supported sports
2. Game scores and winners
3. Key highlights and important plays
4. Formatted in easy-to-read tables

### Changing Email Template
Edit the `send_email()` method in `sports_emailer.py` to customize:
- Email subject line
- HTML styling and layout
- Personal message content
- Table formatting and colors

### Modifying Sports Coverage
You can easily:
- Add or remove sports from the email
- Change the number of days for recent games
- Customize which statistics are displayed
- Add team-specific information or highlights

## Troubleshooting

### Common Issues

**"Authentication failed" error:**
- Check your email/password combination
- For Gmail, ensure you're using an App Password, not your regular password
- Verify 2-factor authentication is enabled

**"API unavailable" errors:**
- Check the GitHub Actions logs for specific error messages
- Verify the ESPN APIs are accessible
- The system will show error messages instead of using fallback data

**Email not received:**
- Check spam/junk folders
- Verify recipient email address is correct
- Check GitHub Actions logs for errors

### Debug Mode
To test locally:

1. Install Python dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   ```bash
   export SENDER_EMAIL="your@email.com"
   export SENDER_PASSWORD="your_password"
   export RECIPIENT_EMAIL="friend@email.com"
   ```
3. Run: `python sports_emailer.py`

## Security Notes

- **Never commit email credentials** to the repository
- Use GitHub Secrets for all sensitive information
- App passwords are more secure than regular passwords
- Consider using environment-specific email accounts

## Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Verify all secrets are set correctly
3. Test the email configuration locally
4. Check API status for the sports data sources

## License

This project is open source. Feel free to modify and share!

---