# 🚀 CareConnect - Quick Reference Card

## 📍 Access URLs
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🔐 Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Patient | patient@careconnect.health | password123 |
| Admin | admin@careconnect.health | admin123 |

## 🎨 AUB Theme Colors
| Color | HEX | Usage |
|-------|-----|-------|
| Berytus Red | #840132 | Primary (buttons, active states) |
| Black | #000000 | Secondary (text, backgrounds) |
| Light Gray | #808080 | Tertiary (inactive states, borders) |

## 🎤 Voice Features
- **Recording:** Click microphone → Grant permission → Speak → Click to stop
- **Voices:** alloy, echo, fable, onyx, nova, shimmer
- **Max Audio:** 25MB
- **Format:** MP3 output, WebM input

## 📱 Responsive Breakpoints
- **Mobile:** < 600px (hamburger menu, 140px voice button)
- **Tablet:** 600-960px (adaptive layout)
- **Desktop:** > 960px (sidebar, 180px voice button)

## 🐳 Docker Commands
```powershell
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker logs careconnect-backend --tail 50

# Restart service
docker-compose restart backend

# Stop all
docker-compose down

# Fresh start (clears data)
docker-compose down -v
docker-compose up -d
```

## ✅ Health Checks
```powershell
# Backend health
curl http://localhost:8000/healthz
# Should return: {"status":"healthy"}

# Container status
docker-compose ps
# All should show "Up" or "healthy"
```

## 🧪 Quick Test Flow
1. Open http://localhost:5173
2. Click "Login as Patient"
3. Go to Chat page
4. Click microphone icon
5. Record message
6. Verify transcription + TTS response

## 🐛 Common Issues
| Issue | Solution |
|-------|----------|
| Containers not starting | `docker-compose down -v && docker-compose up -d` |
| Voice not working | Check microphone permissions in browser |
| Theme not loading | Clear browser cache (Ctrl+Shift+Del) |
| Backend errors | Check `docker logs careconnect-backend` |

## 📚 Documentation
- **Testing Guide:** `TESTING_CHECKLIST.md`
- **Deployment Summary:** `DEPLOYMENT_SUMMARY.md`
- **Voice System:** `docs/VOICE_SYSTEM.md`
- **AUB Theme:** `docs/AUB_THEME_GUIDE.md`

## 🎯 Success Indicators
✅ All containers running and healthy  
✅ Frontend loads with AUB theme  
✅ Login works with demo accounts  
✅ Voice recording and playback functional  
✅ Mobile responsive navigation works  
✅ No console errors  

---

**Status:** ✅ **READY FOR DEMO**  
**Last Updated:** October 31, 2025
