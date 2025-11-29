# CareConnect Demo - User Script

**Instructions:** Copy and paste each message into the chat interface in order. Wait for the agent's response before proceeding to the next message.

---

## Demo Flow

(Red Aub wallpaper)
CareConnect - Smart Health Assistant 
 > Facility Information
 > Finding Doctors
 > Booking an Appointment
 > Book a Lab Test
 > View My Appointments
 > Modify an Appointment
 > Cancel an Appointment
 (animation ybayno we7di wara l teni)

### Part 1: Getting Started
1. `Hi! I'm new here. What can you help me with?`

### Part 2: Facility Information (RAG)
2. `Where can I park when I come to the hospital?`
3. `What are the laboratory hours?`

### Part 3: Finding Doctors
4. `Who are the doctors in the Cardiology department?`
5. `Tell me more about Dr. Sara Haddad`

### Part 4: Booking an Appointment
6. `I need to book an appointment with a cardiologist next Monday`
7. `The 10:00 AM slot with Dr. Sara Haddad works for me`

(shows the appointment in the appointment list + calender)

### Part 5: Lab Test Booking
8. `I need to schedule a lipid panel blood test`
9. `Tomorrow morning at 9am`

### Part 6: View My Appointments
10. `Show me my upcoming appointments`

### Part 7: Modify an Appointment
11. `I need to reschedule my cardiology appointment to the next day, at the same time`

### Part 8: Cancel an Appointment
12. `I need to cancel my lab test appointment`

(shows the appointment in the appointment list + calender)

(Red Aub wallpaper Title: Safety Boundaries)

### Part 9: Safety Boundaries
14. `I have severe chest pain and difficulty breathing`
15. `What medicine should I take for my headache?`
16. `I have a fever and cough. Do I have COVID?`

(Red Aub wallpaper Title: Guiding user to the correct department (fik t8ayer l title))

### Part 10: Multi-turn Conversation
17. `I need to see a doctor`
18. `I've been having knee pain lately`
19. `Sometime next week would be great`
20. `Wednesday at 11 AM looks good`

(Red Aub wallpaper Title: Multilingual suuport)

### Part 11: Arabic Language Support
21. `مرحبا، بدي احجز موعد عند دكتور قلب`
'أرغب في حجز موعد مع الدكتور جيمس تشين يوم الخميس القادم.
22. `Hi, بدي appointment عند الـ dermatology يوم Thursday`

(Red Aub wallpaper Title: Human Support at any time)

### Part 12: Human Support
23. (click on the button and show the support dialog)

(Red Aub wallpaper Title: Voice Support)

### Part 13: Voice Support
24. turn down music, ask anything and record the reply as well

(Red Aub wallpaper Title: Whatsapp Support)

### Part 14: Whatsapp Support
24. I will send you an short of my whastapp convo

---

## Quick Demo (5 Messages)

If you only have a few minutes, use these key messages:

1. `Where can I park at the hospital?`
2. `Who are the doctors in Cardiology?`
3. `Book me an appointment with Dr. Sara Haddad tomorrow at 10 AM`
4. `Show me my appointments`
5. `I have severe chest pain`

---

## Expected Highlights

| # | User Message | What to Observe |
|---|--------------|-----------------|
| 2 | Parking query | Agent retrieves info from RAG |
| 4 | List doctors | Agent queries database |
| 7 | Select time slot | Agent confirms booking with code |
| 9 | Lab test | Auto-routes to Laboratory dept |
| 14 | Chest pain | Immediate 911 emergency response |
| 15 | Medicine advice | Agent refuses medical advice |
| 21 | Arabic message | Agent responds in Arabic |
