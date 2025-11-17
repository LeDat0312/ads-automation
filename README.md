# Facebook Ads Automation System

## 🚀 Quick Deploy to VPS

### One-line deployment:
```bash
curl -sSL https://raw.githubusercontent.com/LeDat0312/ads-automation/main/quick-deploy.sh | sudo bash
```

### Manual deployment:
```bash
git clone https://github.com/LeDat0312/ads-automation.git
cd ads-automation
sudo bash deploy.sh production
```

## 📊 Features

- **Modern Dashboard** - Beautiful, responsive UI with real-time data
- **Facebook Ads API Integration** - Automated campaign management
- **Telegram Bot** - Notifications and alerts
- **Advanced Analytics** - Performance tracking and insights
- **Rule-based Automation** - Smart campaign optimization
- **Multi-account Support** - Manage multiple ad accounts
- **Real-time Monitoring** - Live campaign status updates

## 🛠 Tech Stack

- **Backend**: FastAPI, Python 3.11, SQLAlchemy
- **Frontend**: Modern HTML5, CSS3, Vanilla JavaScript
- **Database**: PostgreSQL with Redis caching
- **Infrastructure**: Nginx, Supervisor, Ubuntu/Debian
- **APIs**: Facebook Graph API, Telegram Bot API

## 📋 Requirements

- Ubuntu 20.04+ or Debian 11+
- 2GB RAM (4GB recommended)
- 20GB storage
- Public IP or domain

## 🎯 Getting Started

1. **Deploy to VPS** using the one-liner above
2. **Configure environment** variables in `.env`
3. **Setup Facebook App** and get API credentials
4. **Create Telegram Bot** for notifications
5. **Access dashboard** at your domain/IP

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Dashboard Design](DASHBOARD_DESIGN.md)
- [Automation Roadmap](AUTOMATION_ROADMAP.md)

## 🔧 Management Commands

```bash
# Update application
sudo bash /var/www/ads-automation/update.sh

# Check status
sudo supervisorctl status

# View logs
sudo tail -f /var/log/ads-automation-production.log

# Backup
sudo /opt/backups/backup-ads-automation.sh
```

## 📞 Support

For issues and support:
- [GitHub Issues](https://github.com/LeDat0312/ads-automation/issues)
- [Documentation](DEPLOYMENT_GUIDE.md)

---

**Made with ❤️ by GitHub Copilot**