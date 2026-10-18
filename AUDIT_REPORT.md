# AUDIT REPORT
**Project:** InventoryTracker  
**Date:** 2026-10-18  
**L2L Phase:** AUDIT  
**Audited by:** Bob `/l2l-audit` mode  

---

## Summary

| Dimension  | Findings | Critical | High | Medium | Low |
|------------|----------|----------|------|--------|-----|
| Security   | 6        | 2        | 2    | 1      | 1   |
| Complexity | 2        | 0        | 2    | 0      | 0   |
| Coverage   | 7        | 0        | 0    | 7      | 0   |
| API Gaps   | 5        | 0        | 3    | 2      | 0   |

**Overall Modernization Score (baseline):** 23 / 100 — **Critical**

Score breakdown:
| Dimension             | Points Earned | Max |
|-----------------------|---------------|-----|
| CVE remediation       | 12            | 30  |
| Test coverage         | 0             | 25  |
| REST API enablement   | 0             | 20  |
| Complexity reduction  | 11            | 15  |
| Framework currency    | 0             | 10  |
| **Total**             | **23**        | 100 |

---

## 1. Security

| Severity | File | Line | Pattern | Description |
|----------|------|------|---------|-------------|
| **CRITICAL** | `ProductController.java` | 58–63 | SQL injection via string concat | `listProducts()` builds a LIKE query by directly interpolating `query` and `sort` request params into SQL using string concatenation on a raw `JdbcTemplate.query()` call. Both `query` (three columns) and `sort` (ORDER BY clause) are attacker-controlled. CVE class: CWE-89. |
| **CRITICAL** | `StringUtils.java` | 93–106 | Unsafe Java deserialization | `deserializeState()` deserializes a base64-encoded object from an untrusted request parameter using `ObjectInputStream` with no class filtering or allowlist. Enables remote code execution. CVE class: CWE-502. |
| **HIGH** | `pom.xml` | 64–65 | CVE in Log4j 1.2.17 | `log4j:log4j:1.2.17` is EOL and carries multiple critical CVEs (CVE-2019-17571 SocketServer RCE, CVE-2020-9488 SMTP appender, CVE-2022-23302/3/5 JMSSink/JDBCAppender/Chainsaw). Should be replaced with SLF4J + Logback. |
| **HIGH** | `pom.xml` | 69–72 | CVE in jackson-databind 2.9.5 | Multiple deserialization gadget CVEs: CVE-2018-7489, CVE-2019-14379, CVE-2019-14540, CVE-2019-17267 among others in 2.9.x. Must be upgraded to 2.15+ or replaced by Spring Boot 3 managed BOM. |
| **MEDIUM** | `pom.xml` | 94–96 | CVE in H2 1.4.196 | CVE-2021-42392 and CVE-2022-45868 affect H2 console. Should be pinned to 2.2.x. |
| **LOW** | `ProductController.java` | 192–198 | Broken export-token check | `exportCsv()` skips the invalid-token rejection when `storedToken == null`, meaning unauthenticated callers (no session, no `exportToken` attribute) can export the full inventory with any arbitrary or empty token. |

### CVE Summary

| CVE(s) | Dependency | Severity |
|--------|------------|----------|
| CVE-2019-17571, CVE-2020-9488, CVE-2022-23302, CVE-2022-23303, CVE-2022-23305 | log4j 1.2.17 | Critical/High |
| CVE-2018-7489, CVE-2019-14379, CVE-2019-14540, CVE-2019-17267 | jackson-databind 2.9.5 | High |
| CVE-2021-42392, CVE-2022-45868 | h2 1.4.196 | High/Medium |

**Total distinct CVE families: 6** (used as `--cve-count` for scoring)

---

## 2. Complexity

| Severity | File | Method | Cyclomatic Complexity (est.) | Threshold |
|----------|------|--------|------------------------------|-----------|
| **HIGH** | `ProductController.java` | `listProducts()` | ~7 | 5 |
| **HIGH** | `ProductController.java` | `exportCsv()` | ~8 | 5 |

**Notes:**
- `listProducts()`: branches on `query != null`, `query.isEmpty()`, `category != null/isEmpty`, paging arithmetic — CC ≈ 7.
- `exportCsv()`: branches on `exportEnabled`, token null/mismatch, `storedToken == null`, category presence, format equality, fields equality — CC ≈ 8.
- All other methods (`viewProduct`, `createProduct`, `editProductForm`, `updateProduct`, `deleteProduct`, `adjustStock`, `DashboardController.index`) are ≤ 5.

---

## 3. Coverage

No test sources exist in the repository. `src/test/` is entirely absent.

| Severity | Module | Class | Uncovered Public Methods | Notes |
|----------|--------|-------|--------------------------|-------|
| MEDIUM | controller | `ProductController` | listProducts, viewProduct, newProductForm, createProduct, editProductForm, updateProduct, deleteProduct, exportCsv, lowStock, adjustStock | 10 public handler methods, 0 tests |
| MEDIUM | controller | `DashboardController` | index | 1 public handler method, 0 tests |
| MEDIUM | service | `ProductService` | getAllProducts, getProductById, getProductsByCategory, saveProduct, deleteProduct, getLowStockProducts, getCategories | 7 public methods, 0 tests |
| MEDIUM | dao | `ProductDao` | findAll, findById, findByCategory, save, deactivate, findAllCategories | 6 public methods, 0 tests |
| MEDIUM | model | `Product` | isLowStock | business logic method, 0 tests |
| MEDIUM | util | `StringUtils` | isBlank, clean, escapeCsv, truncate, join, toLabel, deserializeState, serializeState | 8 public methods, 0 tests |
| MEDIUM | model | `StockMovement` | (all accessors) | 0 tests |

**Test coverage: 0.0% — no test sources at all.**

---

## 4. API Gaps

No REST API layer exists. The application exposes only JSP/MVC handler methods with no `@RestController` or `@ResponseBody` REST endpoints. Zero of the controller actions have a `/api/**` parallel.

| Severity | File | Line | Legacy API / Pattern | Recommended Migration |
|----------|------|------|----------------------|-----------------------|
| **HIGH** | `ProductController.java` | 46 | `@GetMapping` JSP list — no REST equivalent | Add `GET /api/products` returning `ResponseEntity<Page<ProductDto>>` |
| **HIGH** | `ProductController.java` | 103 | `@GetMapping("/{id}")` JSP detail — no REST equivalent | Add `GET /api/products/{id}` returning `ResponseEntity<ProductDto>` |
| **HIGH** | `ProductController.java` | 126,152,166 | POST create/update/delete JSP-only | Add `POST /api/products`, `PUT /api/products/{id}`, `DELETE /api/products/{id}` |
| MEDIUM | `DashboardController.java` | 26 | Dashboard metrics JSP-only | Add `GET /api/dashboard/metrics` returning JSON summary |
| MEDIUM | `ProductController.java` | 260 | Stock adjust JSP-only | Add `PATCH /api/products/{id}/stock` |

**REST API surface coverage: 0.0%**

---

## 5. Dependency Audit (unpinned / outdated)

| Dependency | Version in pom.xml | Status |
|------------|--------------------|--------|
| `log4j:log4j` | 1.2.17 | **EOL — replace with SLF4J+Logback** |
| `jackson-databind` | 2.9.5 | **CVEs — upgrade to 2.15+** |
| `com.h2database:h2` | 1.4.196 | **CVEs — upgrade to 2.2+** |
| `commons-collections:commons-collections` | 3.2.1 | HIGH — gadget chain vectors; upgrade to 4.x |
| `commons-dbcp:commons-dbcp` | 1.4 | **EOL — replace with HikariCP** |
| `commons-lang:commons-lang` | 2.6 | Superseded by commons-lang3 |
| `org.springframework:*` | 4.3.30 | **EOL — target Spring Boot 3.2** |
| `javax.servlet:javax.servlet-api` | 3.1.0 | **Replace with `jakarta.servlet-api` 6.x** |
| `javax.servlet.jsp:javax.servlet.jsp-api` | 2.3.1 | Replace with Jakarta equivalent |
| `javax.servlet:jstl` | 1.2 | Replace with `jakarta.servlet.jsp.jstl` 3.x |
| `tomcat7-maven-plugin` | 2.2 | Use Spring Boot embedded Tomcat |

---

## 6. Javax → Jakarta Namespace

All source files use `javax.servlet.*` imports. Spring Boot 3 requires `jakarta.*`. Affected files:

- [`ProductController.java`](../InventoryTracker Demo Target/src/main/java/com/acme/inventory/controller/ProductController.java:15) — `javax.servlet.http.HttpServletRequest`, `HttpServletResponse`

---

## 7. Logger Declaration Non-Conformance

All classes use `org.apache.log4j.Logger.getLogger(...)`. After migration, the required pattern is:
```java
private static final Logger log = LoggerFactory.getLogger(ClassName.class);
```
Affected: `ProductController`, `DashboardController`, `ProductService`, `ProductDao`, `StringUtils` (5 classes).

---

## 8. Migration Module Order (recommended)

Based on dependency graph and risk:

| Priority | Module | Rationale |
|----------|--------|-----------|
| 1 | `util/StringUtils` | Remove deserializeState RCE, no dependencies |
| 2 | `dao/ProductDao` | Low risk, all queries already parameterized |
| 3 | `service/ProductService` | Thin service layer, delegates to DAO |
| 4 | `controller/ProductController` | SQL injection fix + REST API addition |
| 5 | `controller/DashboardController` | Dashboard metrics REST endpoint |
| 6 | `pom.xml` + build | Dependency upgrades, javax→jakarta, WAR→JAR |

---

## Module VERIFY Log

<!-- Populated during VERIFY phase — one section per transformed module -->

### Module: StringUtils
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS
- **Contract test:** `StringUtilsContractTest` — 24/24
- **Score delta:** —
- **Notes:** Removed `deserializeState` (CWE-502 RCE) and `serializeState`. SLF4J logger. No callers found.

### Module: ProductDao
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS
- **Contract test:** `ProductDaoContractTest` — 13/13
- **Score delta:** —
- **Notes:** SLF4J logger only. All queries were already parameterized.

### Module: ProductService
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS
- **Contract test:** `ProductServiceContractTest` — 15/15
- **Score delta:** —
- **Notes:** SLF4J logger only. Business logic unchanged.

### Module: ProductController
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS
- **Contract test:** `ProductControllerContractTest` — 19/19
- **Score delta:** —
- **Notes:** SQL injection fixed (parameterized LIKE + sort allowlist). Export-token bypass fixed. `listProducts` CC 7→4; `exportCsv` CC 8→3 via private helpers. REST API added (`/api/products` GET/POST/PUT/DELETE/PATCH-stock). `javax.servlet` → `jakarta.servlet`. Full suite: 71/71.

### Module: DashboardController
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS (SLF4J logger — covered by full suite)
- **Score delta:** —
- **Notes:** Logger swap committed as part of StringUtils VERIFY pass. REST endpoint pending DashboardController-specific transform.

### Module: pom.xml / Dependencies
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS
- **Contract test:** DEP-05/DEP-06 — `dependency:resolve` + 71/71 tests
- **Score delta:** 82 → 92 after framework module
- **Notes:** `commons-collections 3.2.1→4.4`, `jackson-databind 2.9.5→2.15.3`, `h2 1.4.196→2.2.224`. log4j already removed in M1.

### Module: pom.xml / Framework
- **Transform date:** 2026-10-18
- **VERIFY status:** ✅ PASS
- **Contract test:** FW-10 — 71/71 tests pass on Spring Boot 3.2.5 + Java 17
- **Score delta:** 82 → 92 (+10 framework currency)
- **Notes:** `spring-boot-starter-parent 3.2.5`, WAR→JAR, `InventoryTrackerApplication` main class added, `application.properties` migrated to Boot keys, HikariCP replaces commons-dbcp, tomcat7 plugin removed.

---

*Generated by L2L `/l2l-audit` mode. Do not edit manually.*
