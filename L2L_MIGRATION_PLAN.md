# L2L Migration Plan — InventoryTracker
**Generated:** 2026-10-18  
**Source:** `AUDIT_REPORT.md` + `pipeline/l2l.config.json`  
**Baseline Score:** 23 / 100 — Critical  
**Target Score:** ≥ 85 / 100 — Modern  

---

## Source → Target Stack

| Dimension        | Source (today)             | Target                        |
|------------------|----------------------------|-------------------------------|
| Java             | 8 (1.8)                    | 17                            |
| Framework        | Spring MVC 4.3.30 (WAR)    | Spring Boot 3.2.x (JAR)       |
| Logging          | Log4j 1.2.17               | SLF4J + Logback               |
| Build / Deploy   | Maven WAR + Tomcat plugin  | Maven JAR + embedded Tomcat   |
| Servlet API      | javax.servlet 3.1          | jakarta.servlet 6.x           |
| DB pool          | commons-dbcp 1.4           | HikariCP (Boot-managed)       |
| JSON             | jackson-databind 2.9.5     | jackson-databind 2.15+ (BOM)  |
| H2               | 1.4.196                    | 2.2.x                         |

---

## Scoring Targets by Dimension

| Dimension            | Baseline | Target | Max | Notes |
|----------------------|----------|--------|-----|-------|
| CVE remediation      | 12       | 30     | 30  | Resolve all 6 CVE families |
| Test coverage        | 0        | 22     | 25  | Contract tests for all 6 modules (≥ 88%) |
| REST API enablement  | 0        | 18     | 20  | 5 REST endpoints alongside JSP controllers |
| Complexity reduction | 11       | 15     | 15  | Refactor `listProducts` + `exportCsv` to CC ≤ 5 |
| Framework currency   | 0        | 10     | 10  | Complete Spring Boot 3 migration |
| **Total**            | **23**   | **95** | 100 |                               |

---

## Module Execution Order

Modules must be transformed and verified strictly in this order. A module may not
advance to the next until its `[Module]ContractTest.java` passes (`mvn test`).

| # | Module              | Phase Gate                               | Primary Findings Addressed                         |
|---|---------------------|------------------------------------------|----------------------------------------------------|
| 1 | `util/StringUtils`  | StringUtilsContractTest passes           | CWE-502 RCE (`deserializeState`), Log4j→SLF4J      |
| 2 | `dao/ProductDao`    | ProductDaoContractTest passes            | Log4j→SLF4J, javax→jakarta (prep)                 |
| 3 | `service/ProductService` | ProductServiceContractTest passes   | Log4j→SLF4J, `getLowStockProducts` coverage       |
| 4 | `controller/ProductController` | ProductControllerContractTest passes | CWE-89 SQL injection, CC reduction, REST API, export-token fix, javax→jakarta |
| 5 | `controller/DashboardController` | DashboardControllerContractTest passes | Log4j→SLF4J, REST API (`/api/dashboard/metrics`) |
| 6 | `pom.xml` / build   | `mvn clean test` green on Spring Boot 3  | All CVEs resolved, WAR→JAR, framework currency    |

---

## Module 1 — `util/StringUtils`

**File:** `src/main/java/com/acme/inventory/util/StringUtils.java`  
**Commit subject:** `L2L[TRANSFORM]: StringUtils — remove deserializeState RCE, SLF4J logger — CVEs: CVE-2019-17571,CVE-2022-23302`

### Contracts to record in `L2L_CONTRACTS.md` before editing

| ID | Contract |
|----|----------|
| SU-01 | `isBlank(null)` returns `true`; `isBlank("")` returns `true`; `isBlank("x")` returns `false` |
| SU-02 | `clean(null)` returns `""`; `clean("  hi  ")` returns `"hi"` |
| SU-03 | `escapeCsv` wraps in quotes when value contains `,`, `"`, or `\n`; double-escapes inner quotes |
| SU-04 | `truncate("abcde", 4)` returns `"a..."`; truncate of a short string is a no-op |
| SU-05 | `join(["a","b"], ",")` returns `"a,b"`; `join(empty, ",")` returns `""` |
| SU-06 | `toLabel("unitPrice")` returns `"Unit Price"`; blank input returns `""` |
| SU-07 | `deserializeState` and `serializeState` are removed; any call site must be deleted or replaced |

### Transform steps

1. Replace `import org.apache.log4j.Logger;` with SLF4J imports.
2. Change logger declaration to:  
   `private static final Logger log = LoggerFactory.getLogger(StringUtils.class);`
3. **Delete** `deserializeState(String encoded)` entirely — no replacement.
4. **Delete** `serializeState(Object obj)` entirely — no replacement.
5. Remove `java.io.ObjectInputStream`, `java.io.ObjectOutputStream`, `java.io.ByteArrayInputStream` imports.
6. Confirm no callers of `deserializeState`/`serializeState` exist anywhere in the codebase (grep required).

### Verify gate

`src/test/java/com/acme/inventory/util/StringUtilsContractTest.java` — unit tests for SU-01 through SU-06, plus a negative test confirming neither deleted method compiles.

---

## Module 2 — `dao/ProductDao`

**File:** `src/main/java/com/acme/inventory/dao/ProductDao.java`  
**Commit subject:** `L2L[TRANSFORM]: ProductDao — SLF4J logger, javax→jakarta prep — CVEs: NONE`

### Contracts to record in `L2L_CONTRACTS.md` before editing

| ID | Contract |
|----|----------|
| PD-01 | `findAll()` returns only active products (`active = 1`), ordered by name |
| PD-02 | `findById(id)` returns `null` when the product does not exist or is inactive |
| PD-03 | `findByCategory(cat)` returns only active products in the given category |
| PD-04 | `save(product)` with `id == null` inserts a new row; returns row-count 1 |
| PD-05 | `save(product)` with `id != null` updates the existing row; returns row-count 1 |
| PD-06 | `deactivate(id)` sets `active = 0`; the row still exists in the table |
| PD-07 | `findAllCategories()` returns distinct, ordered category strings |

### Transform steps

1. Replace `import org.apache.log4j.Logger;` with SLF4J imports.
2. Update logger declaration pattern.
3. No logic changes required — all queries are already parameterized.

### Verify gate

`src/test/java/com/acme/inventory/dao/ProductDaoContractTest.java` — `@SpringBootTest` + in-memory H2 for PD-01 through PD-07.

---

## Module 3 — `service/ProductService`

**File:** `src/main/java/com/acme/inventory/service/ProductService.java`  
**Commit subject:** `L2L[TRANSFORM]: ProductService — SLF4J logger — CVEs: NONE`

### Contracts to record in `L2L_CONTRACTS.md` before editing

| ID | Contract |
|----|----------|
| PS-01 | `saveProduct(product)` throws `IllegalArgumentException` when SKU is blank |
| PS-02 | `saveProduct(product)` throws `IllegalArgumentException` when name is blank |
| PS-03 | `saveProduct(product)` throws `IllegalArgumentException` when `unitPrice < 0` |
| PS-04 | `saveProduct(product)` delegates to `productDao.save()` when all fields are valid |
| PS-05 | `deleteProduct(id)` delegates to `productDao.deactivate(id)` |
| PS-06 | `getLowStockProducts()` returns only products where `quantityOnHand <= reorderPoint` |
| PS-07 | `getProductsByCategory(null)` and `getProductsByCategory("")` both return all products |

### Transform steps

1. Replace `import org.apache.log4j.Logger;` with SLF4J imports.
2. Update logger declaration pattern.
3. No logic changes required.

### Verify gate

`src/test/java/com/acme/inventory/service/ProductServiceContractTest.java` — JUnit 5 with Mockito-mocked `ProductDao` for PS-01 through PS-07.

---

## Module 4 — `controller/ProductController`

**File:** `src/main/java/com/acme/inventory/controller/ProductController.java`  
**Commit subject:** `L2L[TRANSFORM]: ProductController — SQL injection fix, CC reduction, REST API, export-token fix, SLF4J, javax→jakarta — CVEs: CWE-89`

### Contracts to record in `L2L_CONTRACTS.md` before editing

| ID | Contract |
|----|----------|
| PC-01 | `GET /products?q=widget` returns only products matching the search term — **via parameterized query** |
| PC-02 | `GET /products?sort=<injected>` does not execute injected SQL; `sort` is validated against an allowlist (`name`, `sku`, `category`, `unit_price`, `quantity_on_hand`) |
| PC-03 | `GET /products/{id}` returns 200 for a known product; returns the error view for an unknown id |
| PC-04 | `POST /products/create` with a valid product redirects to `/products` |
| PC-05 | `POST /products/create` with blank SKU redirects back with an error flash |
| PC-06 | `POST /products/{id}/adjust` with `delta` that would produce negative stock is rejected |
| PC-07 | `GET /products/export` with no session token returns 403 |
| PC-08 | `GET /api/products` returns HTTP 200 with JSON array |
| PC-09 | `GET /api/products/{id}` returns HTTP 200 with JSON object for a known id; 404 for unknown |
| PC-10 | `POST /api/products` accepts JSON body; returns 201 on success, 400 on validation failure |
| PC-11 | `PUT /api/products/{id}` updates and returns 200; 404 for unknown |
| PC-12 | `DELETE /api/products/{id}` returns 204 |
| PC-13 | `PATCH /api/products/{id}/stock` applies delta; rejects negative result with 422 |

### Transform steps

1. Replace `import org.apache.log4j.Logger;` with SLF4J imports; update logger declaration.
2. Replace `import javax.servlet.*;` with `import jakarta.servlet.*;`.
3. **Fix SQL injection in `listProducts()`:**
   - Extract a private `buildSearchSql(String sort)` helper that validates `sort` against an allowlist and returns the fixed SQL template.
   - Use `?` placeholders for all three `LIKE` parameters; pass `"%" + query.toLowerCase() + "%"` as bound args.
   - This reduces `listProducts()` CC from ~7 to ≤ 5.
4. **Fix export-token bypass in `exportCsv()`:**
   - Remove the `if (storedToken != null)` guard — always reject when token is null or doesn't match.
   - Extract private helpers `resolveExportProducts(String category)` and `writeCsvAll/writeCsvMinimal(PrintWriter, List<Product>)` to reduce CC from ~8 to ≤ 5.
5. **Add REST API alongside existing JSP controller** (do NOT remove JSP mappings):
   - Add inner `@RestController @RequestMapping("/api/products")` class `ProductApiController` (or a separate file `ProductApiController.java`) with endpoints for PC-08 through PC-13.
   - Return `ResponseEntity<?>` for all REST endpoints.
   - Introduce `ProductDto` record/class for JSON projection (id, sku, name, category, unitPrice, quantityOnHand, reorderPoint, supplierCode, active).

### Verify gate

`src/test/java/com/acme/inventory/controller/ProductControllerContractTest.java` — `@SpringBootTest` + `MockMvc` for PC-01 through PC-13.

---

## Module 5 — `controller/DashboardController`

**File:** `src/main/java/com/acme/inventory/controller/DashboardController.java`  
**Commit subject:** `L2L[TRANSFORM]: DashboardController — SLF4J logger, REST metrics endpoint — CVEs: NONE`

### Contracts to record in `L2L_CONTRACTS.md` before editing

| ID | Contract |
|----|----------|
| DC-01 | `GET /` renders the `index` view and populates `totalProducts`, `lowStockCount`, `outOfStockCount`, `totalValue`, `byCategory` model attributes |
| DC-02 | `GET /` does not throw when any DB query returns `null` — attributes default to 0 / 0.0 |
| DC-03 | `GET /api/dashboard/metrics` returns HTTP 200 with JSON containing the same five fields |

### Transform steps

1. Replace `import org.apache.log4j.Logger;` with SLF4J imports; update logger declaration.
2. Extract DB metric queries into a private `DashboardMetrics fetchMetrics()` helper record/method.
3. Add `@GetMapping("/api/dashboard/metrics")` method (or separate `@RestController`) returning `ResponseEntity<DashboardMetrics>`.

### Verify gate

`src/test/java/com/acme/inventory/controller/DashboardControllerContractTest.java` — `@SpringBootTest` + `MockMvc` for DC-01 through DC-03.

---

## Module 6 — `pom.xml` / Build

**File:** `pom.xml` (and `src/main/webapp/WEB-INF/web.xml`, `applicationContext.xml`, `dispatcher-servlet.xml`)  
**Commit subject:** `L2L[TRANSFORM]: pom.xml — Spring Boot 3.2, Java 17, SLF4J+Logback, H2 2.2, jackson 2.15, commons-collections4, HikariCP, WAR→JAR — CVEs: CVE-2019-17571,CVE-2020-9488,CVE-2022-23302,CVE-2022-23303,CVE-2022-23305,CVE-2018-7489,CVE-2019-14379,CVE-2019-14540,CVE-2019-17267,CVE-2021-42392,CVE-2022-45868`

### Transform steps

1. Add `spring-boot-starter-parent 3.2.x` as parent POM.
2. Set `<java.version>17</java.version>`.
3. Remove explicit Spring MVC / spring-jdbc / spring-context deps — inherited from Boot BOM.
4. Remove `log4j:log4j:1.2.17`; remove `log4j.properties`; add `src/main/resources/logback-spring.xml`.
5. Remove `jackson-databind 2.9.5` — Boot BOM supplies 2.15+.
6. Upgrade `h2` to `2.2.224`.
7. Replace `commons-collections:commons-collections:3.2.1` with `org.apache.commons:commons-collections4:4.4`.
8. Replace `commons-dbcp:commons-dbcp:1.4` with HikariCP (Boot-managed).
9. Replace `commons-lang:commons-lang:2.6` with `org.apache.commons:commons-lang3:3.14.0`.
10. Replace `javax.servlet-api / jsp-api / jstl` with their `jakarta.*` equivalents.
11. Change `<packaging>war</packaging>` to `jar`.
12. Replace `tomcat7-maven-plugin` with `spring-boot-maven-plugin`.
13. Delete `src/main/webapp/WEB-INF/spring/applicationContext.xml`, `dispatcher-servlet.xml`, `web.xml` — replaced by Spring Boot auto-configuration.
14. Add `src/main/resources/application.properties` entries for H2 datasource, Thymeleaf or JSP resolver, and `app.pageSize` / `app.exportEnabled`.

### Verify gate

`mvn clean test` on the full project must pass with 0 failures after all modules have been transformed.

---

## Contracts File

All contracts above must be written to `L2L_CONTRACTS.md` **before** the corresponding module is edited. The TRANSFORM gate enforces: no contract entry = no source edit.

---

## Score Projection (post-transform)

```
python3 pipeline/scripts/score.py \
  --cve-count 0 \
  --test-coverage 0.88 \
  --api-coverage 0.90 \
  --complexity-violations 0 \
  --framework-current true
```

Expected output: **score ≥ 95, label "Modern"**

---

## Definition of Done

- [ ] All 6 modules transformed and committed with L2L commit format  
- [ ] All 6 `[Module]ContractTest.java` files exist and pass  
- [ ] `mvn clean test` exits 0 on the target repo  
- [ ] `AUDIT_REPORT.md` Module VERIFY Log populated for all 6 modules  
- [ ] `pipeline/scripts/score.py` run and final score file saved to `pipeline/scores/`  
- [ ] `pipeline/scripts/ledger.py` run and `pipeline/L2L_CHANGE_LEDGER.json` generated  
- [ ] No `System.out.println` remaining in any transformed file  
- [ ] No `org.apache.log4j` imports remaining in any transformed file  
- [ ] No `javax.servlet` imports remaining in any transformed file  
