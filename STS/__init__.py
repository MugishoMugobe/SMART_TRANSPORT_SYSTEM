# On MySQL deployments (Namecheap cPanel shared hosting — see
# docs/DEPLOYMENT.md), Django's mysql backend expects the `MySQLdb`
# module, which is `mysqlclient` — a C extension that needs build tools
# most shared-hosting Python environments don't have. PyMySQL is a
# pure-Python drop-in that needs nothing to compile; this shim makes
# Django's backend import it under the name it expects.
#
# Harmless everywhere else: if PyMySQL isn't installed (SQLite/Postgres
# setups don't need it), this quietly does nothing.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
