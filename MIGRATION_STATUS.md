# ABParts Migration Status

## Current Situation

**Old Server:**
- Running ABParts in production
- User: `abparts`
- To be decommissioned after migration

**New Server:**
- IP: 46.62.131.135
- User: `diogo` (with sudo privileges)
- Already running: `aquaculture-app` (interactive map application)
- Goal: Host both aquaculture-app and ABParts

## Migration Strategy

### Phase 1: Port Conflict Detection ⏳ IN PROGRESS
**Status:** Ready to execute

**Action Required:**
1. Transfer `check_server_ports.sh` to new server
2. Run the script to identify port conflicts
3. Share results to determine optimal port configuration

**Command to run on new server:**
```bash
ssh diogo@46.62.131.135
~/check_server_ports.sh > ~/port_check_results.txt
cat ~/port_check_results.txt
```

### Phase 2: Configuration Preparation ⏸️ WAITING
**Status:** Templates ready, waiting for port check results

**Files prepared:**
- ✅ `check_server_ports.sh` - Port detection script
- ✅ `docker-compose.prod.custom-ports.yml` - Docker config template
- ✅ `nginx-abparts-custom-ports.conf` - Nginx config template
- ✅ `.env.production.template` - Environment variables template
- ✅ `MIGRATION_QUICK_START.md` - Step-by-step guide
- ✅ `HETZNER_NEW_SERVER_MIGRATION.md` - Detailed migration guide
- ✅ `PORT_CONFLICT_RESOLUTION.md` - Port conflict strategies

**Next steps after port check:**
1. Update `docker-compose.prod.yml` with available ports
2. Update `nginx-abparts-custom-ports.conf` with matching ports
3. Create `.env.production` with secure credentials

### Phase 3: Data Backup 📋 PENDING
**Status:** Not started

**Tasks:**
1. Backup production database from old server
2. Backup static files (images, uploads)
3. Backup AI assistant database (if applicable)
4. Transfer backups to local machine
5. Transfer backups to new server

### Phase 4: Deployment 🚀 PENDING
**Status:** Not started

**Tasks:**
1. Install Docker on new server (if needed)
2. Transfer ABParts code to new server
3. Configure environment variables
4. Build and start Docker containers
5. Restore database and static files
6. Run database migrations

### Phase 5: Nginx Configuration 🔧 PENDING
**Status:** Not started

**Tasks:**
1. Configure Nginx for ABParts
2. Ensure no conflicts with aquaculture-app Nginx config
3. Test Nginx configuration
4. Reload Nginx

### Phase 6: Testing ✅ PENDING
**Status:** Not started

**Tasks:**
1. Test API endpoints
2. Test frontend access
3. Test AI Assistant (if enabled)
4. Verify all features work
5. Test both aquaculture-app and ABParts

### Phase 7: Production Cutover 🔄 PENDING
**Status:** Not started

**Tasks:**
1. Update DNS (if using domain)
2. Monitor new server
3. Verify everything works
4. Keep old server running for 24-48 hours as backup

### Phase 8: Decommission Old Server 🗑️ PENDING
**Status:** Not started

**Tasks:**
1. Final backup from old server
2. Stop ABParts containers
3. Remove `abparts` user (optional)
4. Archive old server data

## Port Configuration Options

### Option 1: Default Ports (if available)
```yaml
Frontend:     3000
API:          8000
AI Assistant: 8001
```

### Option 2: Alternative Ports (if defaults are taken)
```yaml
Frontend:     3001
API:          8002
AI Assistant: 8003
```

### Option 3: Custom Ports (based on availability)
```yaml
Frontend:     TBD (after port check)
API:          TBD (after port check)
AI Assistant: TBD (after port check)
```

## Nginx Routing Strategy

### Strategy A: Separate Ports (Current Plan)
- Aquaculture-app: Uses its current ports
- ABParts: Uses different ports
- Nginx routes to both based on path or subdomain

### Strategy B: Path-Based Routing
```
http://46.62.131.135/aquaculture/  → Aquaculture-app
http://46.62.131.135/abparts/      → ABParts
```

### Strategy C: Subdomain Routing (Recommended for Production)
```
http://aquaculture.yourdomain.com  → Aquaculture-app
http://abparts.yourdomain.com      → ABParts
```

## Critical Information Needed

### From Port Check (Step 1):
- [ ] Which ports are currently in use?
- [ ] What ports is aquaculture-app using?
- [ ] What Docker containers are running?
- [ ] What Nginx configurations exist?

### For Configuration (Step 2):
- [ ] What ports should ABParts use?
- [ ] Do you have a domain name for ABParts?
- [ ] Should we use path-based or subdomain routing?
- [ ] Do you want SSL certificates?

### For Deployment (Step 3):
- [ ] Database backup from old server
- [ ] Static files backup from old server
- [ ] OpenAI API key (for AI Assistant)
- [ ] SMTP credentials (for email notifications)

## Timeline Estimate

**Assuming no major issues:**

1. **Port Check & Configuration:** 30 minutes
2. **Backup & Transfer:** 1-2 hours (depends on data size)
3. **Deployment:** 1-2 hours
4. **Testing:** 1 hour
5. **Production Cutover:** 30 minutes

**Total:** 4-6 hours

**Recommended approach:** Do this during low-usage hours or weekend.

## Risk Mitigation

### Backup Strategy
- ✅ Keep old server running during migration
- ✅ Create multiple backups before starting
- ✅ Test restoration on new server before cutover
- ✅ Keep local copies of all backups

### Rollback Plan
If migration fails:
1. Keep old server running (don't shut it down)
2. Point DNS back to old server (if changed)
3. Investigate issues on new server
4. Retry migration when ready

### Testing Checklist
Before declaring migration successful:
- [ ] Can login to ABParts
- [ ] Dashboard loads with correct data
- [ ] Can view parts, inventory, machines
- [ ] Can create/edit records
- [ ] Images/uploads are visible
- [ ] AI Assistant works (if enabled)
- [ ] Email notifications work
- [ ] All user roles work correctly
- [ ] Aquaculture-app still works

## Current Status Summary

**✅ Completed:**
- Migration planning
- Documentation created
- Port check script prepared
- Configuration templates ready
- Quick start guide written

**⏳ In Progress:**
- Waiting for port check results from new server

**📋 Next Steps:**
1. **YOU:** Run port check script on new server
2. **YOU:** Share port check results
3. **ME:** Help configure exact ports to use
4. **YOU:** Follow MIGRATION_QUICK_START.md

## Questions to Answer

1. **Port Check Results:** What ports are available on the new server?
2. **Domain Name:** Do you have a domain for ABParts? (e.g., abparts.yourdomain.com)
3. **SSL Certificate:** Do you want HTTPS with SSL certificate?
4. **Routing Preference:** Path-based or subdomain routing for both apps?
5. **Backup Timing:** When can you create backups from old server?
6. **Migration Window:** When do you want to perform the migration?

## Support Files

All files are ready in your local `~/abparts/` directory:

```
abparts/
├── check_server_ports.sh                    # Port detection script
├── docker-compose.prod.custom-ports.yml     # Docker config template
├── nginx-abparts-custom-ports.conf          # Nginx config template
├── .env.production.template                 # Environment template
├── MIGRATION_QUICK_START.md                 # Quick start guide
├── HETZNER_NEW_SERVER_MIGRATION.md          # Detailed guide
├── PORT_CONFLICT_RESOLUTION.md              # Port strategies
└── MIGRATION_STATUS.md                      # This file
```

## Ready to Start?

**First step:** Run the port check script on your new server!

```bash
# Transfer the script
scp check_server_ports.sh diogo@46.62.131.135:~/

# SSH to new server
ssh diogo@46.62.131.135

# Run the script
chmod +x ~/check_server_ports.sh
~/check_server_ports.sh

# Save results
~/check_server_ports.sh > ~/port_check_results.txt

# View results
cat ~/port_check_results.txt
```

Then share the output with me, and we'll proceed with the migration! 🚀
