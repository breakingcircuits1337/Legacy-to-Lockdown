# L2L Contracts
> One section per module. Each contract must exist here **before** the corresponding source file is edited.
> Written by `/l2l-transform` mode. Do not remove completed entries.

---

## Module 1 — `util/StringUtils`

**Source file:** `src/main/java/com/acme/inventory/util/StringUtils.java`  
**Transform date:** 2026-10-18  
**Commit subject:** `L2L[TRANSFORM]: StringUtils — remove deserializeState RCE, SLF4J logger — CVEs: CVE-2019-17571,CVE-2022-23302`

| ID    | Contract |
|-------|----------|
| SU-01 | `isBlank(null)` returns `true`; `isBlank("")` returns `true`; `isBlank("  ")` returns `true`; `isBlank("x")` returns `false` |
| SU-02 | `clean(null)` returns `""`; `clean("  hi  ")` returns `"hi"`; `clean("")` returns `""` |
| SU-03 | `escapeCsv(null)` returns `""`; a plain value with no special chars is returned as-is; a value containing `,` is wrapped in double-quotes; a value containing `"` is wrapped and the inner quote is doubled; a value containing `\n` is wrapped in double-quotes |
| SU-04 | `truncate("abcde", 4)` returns `"a..."`; `truncate("abc", 5)` returns `"abc"` unchanged; `truncate(null, 5)` returns `""` |
| SU-05 | `join(["a","b","c"], ",")` returns `"a,b,c"`; `join(emptyList, ",")` returns `""`; `join(null, ",")` returns `""` |
| SU-06 | `toLabel("unitPrice")` returns `"Unit Price"`; `toLabel("SKU")` returns `"S K U"`; `toLabel(null)` returns `""`; `toLabel("")` returns `""` |
| SU-07 | `deserializeState` does not exist in the transformed class (compilation fails if called) |
| SU-08 | `serializeState` does not exist in the transformed class (compilation fails if called) |

---

## Module 2 — `dao/ProductDao`

**Source file:** `src/main/java/com/acme/inventory/dao/ProductDao.java`
**Transform date:** 2026-10-18
**Commit subject:** `L2L[TRANSFORM]: ProductDao — SLF4J logger — CVEs: NONE`

| ID    | Contract |
|-------|----------|
| PD-01 | `findAll()` returns only active products (`active = 1`), ordered by name |
| PD-02 | `findById(id)` returns `null` when the product does not exist or is inactive |
| PD-03 | `findByCategory(cat)` returns only active products in the given category |
| PD-04 | `save(product)` with `id == null` inserts a new row; returns row-count 1 |
| PD-05 | `save(product)` with `id != null` updates the existing row; returns row-count 1 |
| PD-06 | `deactivate(id)` sets `active = 0`; the row still exists in the table |
| PD-07 | `findAllCategories()` returns distinct, ordered category strings |

---

## Module 3 — `service/ProductService`

**Source file:** `src/main/java/com/acme/inventory/service/ProductService.java`
**Transform date:** 2026-10-18
**Commit subject:** `L2L[TRANSFORM]: ProductService — SLF4J logger — CVEs: NONE`

| ID    | Contract |
|-------|----------|
| PS-01 | `saveProduct(product)` throws `IllegalArgumentException` when SKU is blank |
| PS-02 | `saveProduct(product)` throws `IllegalArgumentException` when name is blank |
| PS-03 | `saveProduct(product)` throws `IllegalArgumentException` when `unitPrice < 0` |
| PS-04 | `saveProduct(product)` delegates to `productDao.save()` when all fields are valid |
| PS-05 | `deleteProduct(id)` delegates to `productDao.deactivate(id)` |
| PS-06 | `getLowStockProducts()` returns only products where `quantityOnHand <= reorderPoint` |
| PS-07 | `getProductsByCategory(null)` and `getProductsByCategory("")` both return all products |

---

## Module 5 — `controller/DashboardController`

**Source file:** `src/main/java/com/acme/inventory/controller/DashboardController.java`
**Transform date:** 2026-10-18
**Commit subject:** `L2L[TRANSFORM]: DashboardController — SLF4J logger — CVEs: NONE`

| ID    | Contract |
|-------|----------|
| DC-01 | `GET /` renders the `index` view and populates `totalProducts`, `lowStockCount`, `outOfStockCount`, `totalValue`, `byCategory` model attributes |
| DC-02 | `GET /` does not throw when any DB query returns `null` — attributes default to 0 / 0.0 |

---

## Module 4 — `controller/ProductController`

**Source file:** `src/main/java/com/acme/inventory/controller/ProductController.java`  
**Transform date:** 2026-10-18  
**Commit subject:** `L2L[TRANSFORM]: ProductController — SQL injection fix, CC reduction, REST API, export-token fix, javax→jakarta — CVEs: CWE-89`

| ID    | Contract |
|-------|----------|
| PC-01 | `GET /products?q=widget` executes a parameterized LIKE query — no string concatenation of `q` into SQL |
| PC-02 | `GET /products?sort=<injected>` rejects any `sort` value not in the allowlist (`name`, `sku`, `category`, `unit_price`, `quantity_on_hand`); defaults to `name` |
| PC-03 | `GET /products/{id}` returns the product view for a known id; returns the error view for an unknown id |
| PC-04 | `POST /products/create` with a valid product redirects to `/products` |
| PC-05 | `POST /products/create` with blank SKU redirects back to `/products/new` with an error flash attribute |
| PC-06 | `POST /products/{id}/adjust` with a `delta` that would produce negative stock is rejected with an error flash attribute |
| PC-07 | `GET /products/export` with no session token AND no stored session token returns HTTP 403 |
| PC-08 | `GET /api/products` returns HTTP 200 with a JSON array |
| PC-09 | `GET /api/products/{id}` returns HTTP 200 with a JSON object for a known id; HTTP 404 for unknown |
| PC-10 | `POST /api/products` with a valid JSON body returns HTTP 201 |
| PC-11 | `POST /api/products` with blank SKU returns HTTP 400 |
| PC-12 | `PUT /api/products/{id}` with a valid JSON body returns HTTP 200 |
| PC-13 | `PATCH /api/products/{id}/stock` with a delta that produces negative stock returns HTTP 422 |

---

## Module 6 — `pom.xml` / Dependencies

**Source file:** `pom.xml`  
**Transform date:** 2026-10-18  
**Commit subject:** `L2L[TRANSFORM]: Dependencies — 4 CVEs remediated — CVEs: CVE-2019-17571,CVE-2015-6420,CVE-2019-14379,CVE-2021-42392`

| ID    | Contract |
|-------|----------|
| DEP-01 | `log4j:log4j` does not appear anywhere in pom.xml after transform |
| DEP-02 | `commons-collections:commons-collections:3.2.1` is replaced by `org.apache.commons:commons-collections4:4.4` |
| DEP-03 | `jackson-databind` version is `2.15.3` or higher; `2.9.5` does not appear |
| DEP-04 | `h2` version is `2.2.224`; `1.4.196` does not appear |
| DEP-05 | `mvn dependency:resolve` exits 0 — all declared dependencies resolve successfully |
| DEP-06 | `mvn test` exits 0 — all 71 existing contract tests still pass after dependency changes |

---

## Module 6b — Framework Migration (Spring Boot 3.2 / Java 17 / JAR)

**Files:** `pom.xml`, `src/main/resources/application.properties`, `src/main/java/com/acme/inventory/InventoryTrackerApplication.java` (new)  
**Transform date:** 2026-10-18  
**Commit subject:** `L2L[TRANSFORM]: Framework — Spring Boot 3.2, Java 17, WAR→JAR, Boot auto-config — CVEs: NONE`

| ID    | Contract |
|-------|----------|
| FW-01 | `<packaging>` is `jar`, not `war` |
| FW-02 | `spring-boot-starter-parent 3.2.x` is the project parent |
| FW-03 | `<java.version>` is `17` |
| FW-04 | `spring-webmvc`, `spring-jdbc`, `spring-context` explicit deps are removed — inherited from Boot BOM |
| FW-05 | `spring-boot-starter-web` and `spring-boot-starter-jdbc` are present |
| FW-06 | `slf4j-api` and `slf4j-simple` explicit deps removed — Boot BOM provides Logback |
| FW-07 | `spring-boot-maven-plugin` present in build; `tomcat7-maven-plugin` removed |
| FW-08 | `application.properties` contains `spring.datasource.*` keys Boot recognises |
| FW-09 | A `@SpringBootApplication` main class exists at `com.acme.inventory.InventoryTrackerApplication` |
| FW-10 | `mvn test` exits 0 — all existing contract tests pass under Spring Boot 3.2 |
