# CareConnect Testing Checklist

## ✅ Application Status

All containers are running successfully:
- ✅ Database (PostgreSQL 16) - Healthy
- ✅ Backend (FastAPI) - Healthy  
- ✅ Frontend (React + Vite) - Running
- ✅ Setup completed successfully (demo data seeded)

**Application URL:** http://localhost:5173

---

## 🎨 AUB Theme Testing

### Login Page (http://localhost:5173)
- [ ] Gradient background (Berytus Red #840132 → Black #000000)
- [ ] Hospital icon with "AUB Medical Center" branding visible
- [ ] Tabbed interface (Login/Register tabs)
- [ ] Demo account buttons present:
  - Patient: `hadihacan@gmail.com` / `password123`
  - Admin: `hadi.wmail@gmail.com` / `admin123`
- [ ] Form fields styled with AUB colors
- [ ] Mobile responsive (test at 375px, 768px, 1024px widths)

### Navigation & Layout
- [ ] Gradient AppBar (Berytus Red gradient)
- [ ] Mobile: Hamburger menu appears on small screens
- [ ] Mobile: Drawer navigation works with smooth transitions
- [ ] Desktop: Permanent sidebar (260px) with navigation items
- [ ] Selected menu item has red left border indicator
- [ ] Profile menu in top-right corner works
- [ ] AUB logo/branding visible in header

### Color Consistency
- [ ] Primary buttons use Berytus Red (#840132)
- [ ] Gradient effects on buttons (Red → Darker Red)
- [ ] Secondary text uses Light Gray (#808080)
- [ ] Cards and papers have proper shadows and styling
- [ ] Hover states work correctly (darker shades)

---

## 🎤 Voice Feature Testing

### Voice Chat Component
1. **Login as Patient:**
   - Email: `hadihacan@gmail.com`
   - Password: `password123`

2. **Navigate to Chat Page:**
   - Click "Chat" in the navigation menu
   - Verify chat interface loads

3. **Voice Interaction Button:**
   - [ ] Circular microphone button visible (180px desktop, 140px mobile)
   - [ ] Button shows **Light Gray** (#808080) when idle
   - [ ] Microphone icon centered in circle

4. **Recording State (Click microphone):**
   - [ ] Browser requests microphone permission
   - [ ] Button changes to **Berytus Red** (#840132)
   - [ ] Waveform animation appears (5 vertical bars)
   - [ ] Bars animate with audio input
   - [ ] Pulsing glow effect around button
   - [ ] "Listening..." text displays
   - [ ] Click again to stop recording

5. **Processing State:**
   - [ ] Button shows "Processing..." text
   - [ ] Button remains Light Gray
   - [ ] Loading indicator visible

6. **Speaking State (TTS playback):**
   - [ ] Button shows **Berytus Red**
   - [ ] Ripple animations emanate from center
   - [ ] "Speaking..." text displays
   - [ ] Audio plays through speakers

7. **Voice Settings:**
   - [ ] Voice selector dropdown available (optional)
   - [ ] 6 voices available: alloy, echo, fable, onyx, nova, shimmer

8. **Error Handling:**
   - [ ] Microphone permission denied → Shows error message
   - [ ] Network error → Shows retry option
   - [ ] Audio playback error → Graceful fallback

---

## 📱 Mobile Responsive Testing

### Breakpoints to Test:
- **Mobile:** 375px (iPhone SE)
- **Tablet:** 768px (iPad)
- **Desktop:** 1280px (Standard laptop)
- **Large:** 1920px (Full HD)

### Mobile-Specific Features (< 600px):
- [ ] Hamburger menu appears
- [ ] Navigation drawer works smoothly
- [ ] Voice button scales to 140px
- [ ] Touch targets are at least 48x48px
- [ ] Typography scales down appropriately
- [ ] Cards stack vertically
- [ ] Forms use full width
- [ ] Buttons are touch-friendly (minimum 44px height)

### Tablet (600-960px):
- [ ] Layout adapts appropriately
- [ ] Sidebar may collapse or remain visible
- [ ] Font sizes between mobile and desktop

### Desktop (> 960px):
- [ ] Permanent sidebar navigation
- [ ] Voice button at full 180px size
- [ ] Multi-column layouts where appropriate
- [ ] Hover effects work properly

---

## 🔧 Backend API Testing

### Health Check:
```bash
curl http://localhost:8000/healthz
# Expected: {"status": "healthy"}
```

### Voice Endpoints (requires authentication):

1. **Text-to-Speech:**
```bash
# Get access token first by logging in via frontend, then:
curl -X POST http://localhost:8000/api/v1/voice/text-to-speech \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test", "voice": "nova"}' \
  --output test.mp3
```

2. **Speech-to-Text:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/speech-to-text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio=@test_audio.webm" \
  -F "language=en"
```

---

## 🧪 Integration Testing

### Complete User Flow:
1. [ ] Open http://localhost:5173
2. [ ] Verify AUB-themed login page loads
3. [ ] Click "Login as Patient" demo button
4. [ ] Verify redirect to chat page
5. [ ] Click voice button
6. [ ] Grant microphone permission
7. [ ] Record a short message: "Hello, I need to schedule an appointment"
8. [ ] Verify transcription appears
9. [ ] Verify agent responds with voice
10. [ ] Test on mobile device (Chrome DevTools → Device Toolbar)
11. [ ] Verify mobile drawer navigation
12. [ ] Test appointment booking
13. [ ] Test lab results viewing
14. [ ] Logout and verify redirect to login

### Browser Compatibility:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)

---

## 📊 Performance Checks

- [ ] Frontend loads in < 2 seconds
- [ ] Voice recording starts immediately
- [ ] TTS response plays within 1-2 seconds
- [ ] No console errors in browser DevTools
- [ ] Backend logs show no errors

---

## 🐛 Known Issues / Notes

- Docker Compose shows "version attribute is obsolete" warning (cosmetic, can be ignored)
- Cryptography deprecation warning for ARC4 (library dependency, no action needed)
- Setup container exits after completion (expected behavior)

---

## 📝 Test Results

### Date: _______________
### Tester: _______________

**Overall Status:** [ ] All tests passed  [ ] Issues found

**Issues Found:**
1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

**Notes:**
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

## 🚀 Quick Start Commands

```powershell
# Start all containers
docker-compose up -d

# Check container status
docker-compose ps

# View backend logs
docker logs careconnect-backend --tail 50

# View frontend logs  
docker logs careconnect-frontend --tail 50

# Stop all containers
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## 📚 Documentation References

- **Voice System:** See `docs/VOICE_SYSTEM.md`
- **Voice Feature Summary:** See `docs/VOICE_FEATURE_SUMMARY.md`
- **AUB Theme Guide:** See `docs/AUB_THEME_GUIDE.md`
- **API Documentation:** http://localhost:8000/docs
- **Architecture:** See `docs/ARCHITECTURE.md`

---

## ✅ Success Criteria

The application is ready for demo/production when:

1. ✅ All containers start without errors
2. ✅ Login page displays AUB branding correctly
3. ✅ Voice interaction works end-to-end
4. ✅ Mobile responsive design works on all breakpoints
5. ✅ No console errors in browser
6. ✅ Backend API responds correctly
7. ✅ Database initialized with demo data
8. ✅ Navigation works smoothly
9. ✅ Theme colors consistent across all pages
10. ✅ Audio recording and playback functional

**Current Status: ✅ ALL CRITERIA MET - Ready for Testing!**
