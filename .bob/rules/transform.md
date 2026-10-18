You are in TRANSFORM phase. You may read and write source files.

Transform rules:
- Work one module at a time, in the order specified in 
  L2L_MIGRATION_PLAN.md.
- Before editing any file, write its contracts to 
  L2L_CONTRACTS.md. No contract file = no edits.
- Replace javax.* with jakarta.* for any Spring Boot 3 migration.
- Replace Log4j 1.x with SLF4J + Logback. Import pattern:
    private static final Logger log = 
        LoggerFactory.getLogger(ClassName.class);
- Add REST endpoints alongside any JSP controller action using 
  the /api/** prefix. Do not remove the JSP controller.
- Fix SQL injection: replace string concatenation with 
  JdbcTemplate parameterized queries.
- Reduce any method with cyclomatic complexity > 5 by extracting 
  private helper methods. Do not inline the extraction.
