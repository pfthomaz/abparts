# Migration Quick Reference Card

## Before Creating Migration

```bash
./pre_migration_check.sh
```

## Create Migration

```bash
# Auto-generate from models
docker-compose exec api alembic revision --autogenerate -m "short description"

# Or create empty
docker-compose exec api alembic revision -m "short description"
```

## Edit Migration File

1. **Check revision ID length** (≤ 32 chars!)
2. **Set correct down_revision** (from previous file's `revision` variable)
3. **Write upgrade() function**
4. **Write downgrade() function**

## Test Migration

```bash
./test_migration.sh
```

## The 3 Golden Rules

1. ✅ **Revision ID ≤ 32 characters**
2. ✅ **Use actual revision ID for down_revision** (not filename)
3. ✅ **Test locally before committing**

## Common Mistakes

| ❌ Wrong | ✅ Right |
|---------|---------|
| `revision = '20241130_redesign_stock_adjustments'` (37 chars) | `revision = '20241130_stock_adj'` (19 chars) |
| `down_revision = '20251124_add_customer_order_id_to_transactions'` | `down_revision = '20251124_order_txn'` |
| No downgrade() function | Always write downgrade() |

## If Migration Fails

1. **Read the error message carefully**
2. **Check revision ID length**
3. **Verify down_revision exists**
4. **Check for multiple heads**: `docker-compose exec api alembic heads`
5. **If multiple heads, create merge migration first**

## Emergency: Rollback

```bash
# Downgrade one step
docker-compose exec api alembic downgrade -1

# Downgrade to specific revision
docker-compose exec api alembic downgrade <revision_id>

# Check current state
docker-compose exec api alembic current
```

---

**Keep this card handy when creating migrations!**
