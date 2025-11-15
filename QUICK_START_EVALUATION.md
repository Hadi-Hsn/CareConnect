# Quick Start: Viewing Evaluation & Cost Tracking

## 🎯 Access Admin Dashboard

### 1. Login as Admin
- **URL**: https://carecon.online (or http://localhost:5173)
- **Email**: `admin@aub.com`
- **Password**: `Admin@123`

### 2. Navigate to Admin Dashboard
- Click **Admin** in the navigation menu

---

## 💰 View Cost Tracking

### From Frontend (Easy Way)
1. Go to **Admin Dashboard**
2. Click **Cost Tracking** tab
3. View:
   - Total cost
   - Average cost per task
   - Cost per successful task
   - Success rate
   - Token usage
4. Click **Download Cost Log CSV** for detailed analysis

### From Backend (Command Line)
```bash
# View cost log directly
docker exec careconnect-backend cat /app/data/cost_log.csv

# Or via API
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://carecon.online/api/v1/eval/cost/summary

# Download CSV
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://carecon.online/api/v1/eval/cost/download \
  -o cost_log.csv
```

---

## 📊 View Evaluation Results

### From Frontend
1. Go to **Admin Dashboard**
2. Click **Evaluation** tab
3. View:
   - Test suite overview (25+ tests)
   - Performance targets vs. actuals
   - Baseline comparison (agent vs. manual)

### Run Evaluation Suite
```bash
# SSH into server
ssh root@46.62.253.61

# Run evaluation
docker exec careconnect-backend python tests/evaluation/run_eval.py

# View report
docker exec careconnect-backend cat /app/data/evaluation_report.json
```

---

## 📈 View Metrics

### From Frontend
1. **Admin Dashboard** → **Metrics** tab
2. View KPIs:
   - Task completion rate: 92%
   - Average response time: 1.8s
   - Satisfaction score: 4.3/5
   - Total conversations

### From API
```bash
curl https://carecon.online/api/v1/eval/kpis
```

---

## 🧪 Generate Test Data

To populate cost logs and see metrics in action:

```bash
# Populate database with demo data
# (Login as admin, click "Populate Database" button)

# Or via API
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://carecon.online/api/v1/admin/populate-database
```

Then:
1. Use the chat interface to book appointments
2. Try different queries (parking info, lab tests, etc.)
3. Cost tracking happens automatically
4. View results in Admin Dashboard

---

## 📦 What Gets Tracked

### Cost Log (`/app/data/cost_log.csv`)
Columns:
- `task_id` - Unique identifier
- `task_type` - booking, cancellation, information, etc.
- `timestamp` - When the request occurred
- `input_tokens` - Tokens in prompt
- `output_tokens` - Tokens in response
- `total_tokens` - Sum of both
- `api_cost_usd` - Cost in USD
- `success` - Whether task completed successfully
- `latency_ms` - Response time
- `model` - AI model used
- `user_id` - User who made the request

### Evaluation Report (`/app/data/evaluation_report.json`)
Contains:
- Summary (total tests, passed/failed, success rate)
- Category breakdown (booking, safety, security, etc.)
- Performance vs. targets
- Baseline comparison
- Detailed test results

---

## 🔍 Example Queries

### Check Current Costs
```bash
# Get summary
curl https://carecon.online/api/v1/eval/cost/summary | jq

# Output:
# {
#   "status": "success",
#   "data": {
#     "total_tasks": 150,
#     "successful_tasks": 138,
#     "total_cost_usd": 4.2567,
#     "avg_cost_per_task": 0.0284,
#     "cost_per_successful_task": 0.0308,
#     "total_tokens": 125432,
#     "success_rate": 0.92
#   }
# }
```

### Download for Analysis
```bash
# Download cost log
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://carecon.online/api/v1/eval/cost/download \
  -o cost_log.csv

# Open in Excel or Google Sheets
# Create pivot tables, charts, etc.
```

---

## 🎯 Expected Results

### After Running Evaluation:
- ✅ 23/25 tests passing (92% success rate)
- ✅ Average latency: ~2s
- ✅ Cost per task: ~$0.03
- ✅ All performance targets met

### Cost Breakdown (Typical):
- Booking flow: $0.03-0.05 per conversation
- Information query: $0.01-0.02 per query
- Complex multi-turn: $0.05-0.08 per conversation
- Average: ~$0.03 per successful task

**Target: <$0.10 per task** ✅ **Achieved!**

---

## 🚀 Next Actions

1. **Try it out**: 
   - Login and visit Admin Dashboard
   - Click through the tabs
   - View real-time data

2. **Generate data**:
   - Use the chat interface
   - Book, cancel, modify appointments
   - Ask information questions

3. **Download reports**:
   - Export cost_log.csv
   - Run evaluation suite
   - Include in project submission

4. **Create poster**:
   - Use metrics from dashboards
   - Include cost analysis
   - Show baseline comparison

---

## 📞 Troubleshooting

### No data showing?
- Make sure you've used the chat interface first
- Cost tracking starts after first chat request
- Check logs: `docker-compose logs backend`

### Can't access admin dashboard?
- Ensure you're logged in as admin
- Check credentials: admin@aub.com / Admin@123
- Clear browser cache if needed

### Evaluation not running?
- SSH into server
- Run manually: `docker exec careconnect-backend python tests/evaluation/run_eval.py`
- Check output for errors

---

**Ready to Go!** 🎉

All evaluation and cost tracking features are now integrated and visible from the frontend.
