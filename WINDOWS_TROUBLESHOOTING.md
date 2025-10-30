# Windows Troubleshooting Guide

## Issue: Frontend Hangs with No Backend Logs

### Root Cause (FIXED)
The issue was caused by a **port mismatch** between the frontend and backend:
- Frontend was configured to connect to port **8501** (`NEXT_PUBLIC_BACKEND_PORT=8501`)
- Backend was actually running on port **8000**

### Quick Fix

1. **Open your `.env` file** in the project root
2. **Make sure ALL port settings match**:

```env
# All three should use the SAME port number
PORT=3000                      # Frontend Next.js port
BACKEND_PORT=8000              # Backend FastAPI port
NEXT_PUBLIC_BACKEND_PORT=8000  # Frontend connects here (MUST match BACKEND_PORT!)
```

3. **Restart both servers** (close terminals and run again):
```bash
npm run dev
```

### How to Verify It's Working

1. **Check Backend Logs**: When you upload a file, you should see:
   ```
   [run_id] Starting processing run: X files...
   [run_id] Saved file: yourfile.pdf to ...
   ```

2. **Check Browser Console** (Press F12 in browser):
   - You should see detailed `[API]`, `[API-URL]`, and `[AnalysisOptions]` logs
   - Look for the line `[API-URL] Generated base URL: http://localhost:XXXX`
   - **This port MUST match where your backend is running!**

3. **Check Network Tab** in Browser DevTools:
   - Should see a `POST` request to `/api/transform`
   - Status should be `200` or show as pending while processing
   - If you see **nothing**, the port is wrong!

### Advanced Diagnostics

If it still doesn't work, check the browser console for these specific logs:

#### Expected Flow:
```
[AnalysisOptions] handleTransform called
[AnalysisOptions] Selected files: 1 ["test.pdf"]
[API] transformFiles called
[API] Files: 1 [{name: "test.pdf", size: 12345, type: "application/pdf"}]
[API-URL] Client-side URL generation
[API-URL] Generated base URL: http://localhost:8000
[API] Sending POST request to http://localhost:8000/api/transform
[API] Response status: 200 OK
[API] Starting to read streaming response...
[API] Event 1: init
```

#### If You See Port Mismatch:
```
[API-URL] Generated base URL: http://localhost:8501  ← WRONG!
```
**Fix**: Update `NEXT_PUBLIC_BACKEND_PORT=8000` in `.env`

#### If You See Connection Error:
```
[API] Exception in transformFiles: TypeError: Failed to fetch
```
**Causes**:
1. Backend not running (check terminal)
2. Port mismatch (check `.env`)
3. Windows Firewall blocking connection (allow Node.js and Python)

#### If FormData Fails:
```
[API] Adding file 1/1: undefined 0 bytes  ← BAD!
```
**Cause**: File selection bug (unlikely on Windows, but possible)
**Fix**: Try different file types or smaller files

### Windows-Specific Notes

1. **Firewall**: Windows may block Node.js or Python. When prompted, click "Allow access"

2. **Antivirus**: Some antivirus software blocks localhost connections. Try:
   - Temporarily disable antivirus
   - Add InfoTransform folder to exclusions

3. **Port Already in Use**:
   ```
   Error: listen EADDRINUSE: address already in use :::8000
   ```
   **Fix**:
   ```bash
   # Find process using the port
   netstat -ano | findstr :8000
   # Kill it (replace PID with actual number)
   taskkill /PID <PID> /F
   ```

4. **Path Issues**: Windows uses backslashes `\`, but the app handles this automatically. No action needed.

### Environment Variables Not Loading?

If `NEXT_PUBLIC_BACKEND_PORT` shows as `undefined` in console:

1. **Restart VS Code** (or your IDE) - it needs to reload `.env`
2. **Restart terminals** - environment variables are loaded on startup
3. **Check `.env` location** - must be in project ROOT, not `frontend/` or `backend/`

### Still Not Working?

Share these logs:
1. Browser console output (copy entire console)
2. Backend terminal output
3. Your `.env` file (remove API keys!)
4. Output of `npm run dev` command

---

## Testing the Fix

### Test 1: Backend Responds
```bash
# Open browser or use curl
curl http://localhost:8000/health

# Expected response:
{"status":"healthy","processors_initialized":true,"server":"FastAPI","version":"2.0.0"}
```

### Test 2: Frontend Connects
```bash
# Open browser to:
http://localhost:3000

# Open DevTools (F12) > Console
# Upload a file and click "Transform to Structured Data"
# You should see [API], [AnalysisOptions], and [API-URL] logs
```

### Test 3: Full Processing
1. Upload a test file (PDF, image, or document)
2. Select a document schema
3. Click "Transform to Structured Data"
4. **Expected**: Processing starts immediately with progress indicators
5. **Backend logs** should show `[run_id] Starting processing run...`

---

## Additional Resources

- **Main README**: `/README.md` - General setup instructions
- **CLAUDE.md**: `/CLAUDE.md` - Developer documentation
- **Environment Example**: `/.env.example` - Reference configuration

## Changes Made to Fix This Issue

### 1. Added Comprehensive Logging
- `frontend/components/AnalysisOptions.tsx` - Logs when transform starts
- `frontend/lib/api.ts` - Logs FormData building, URL, and fetch calls
- `frontend/lib/utils/api-url.ts` - Logs port resolution and URL generation

### 2. Improved Error Handling
- Try-catch blocks around critical sections
- Better error messages showing actual failure points
- Network errors now display user-friendly messages

### 3. Port Validation
- Validates `NEXT_PUBLIC_BACKEND_PORT` is a valid number
- Falls back to 8000 if invalid
- Logs port resolution steps

All logs use prefixes like `[API]`, `[API-URL]`, `[AnalysisOptions]` for easy debugging.

---

**Last Updated**: 2025-10-30
**Issue**: Frontend hangs on Windows with no backend logging
**Status**: Fixed with enhanced diagnostics
