# MISP-CLI Potential Commands Analysis

## Summary

Based on analysis of the MISP OpenAPI specification (https://www.misp-project.org/openapi/) and the current misp-cli codebase, here are the potential commands to add:

---

## 🚨 Priority 1: Completely Missing Command Categories

### 1. Organisations (`organisations.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /organisations/index` | List organisations |
| `GET /organisations/view/{id}` | View organisation details |
| `POST /organisations/add` | Create organisation |
| `POST /organisations/edit/{id}` | Edit organisation |
| `POST /organisations/delete/{id}` | Delete organisation |
| `GET /organisations/fields` | Get organisation fields |

**Use case**: Essential for multi-tenant MISP management, org-level permissions, sharing group management.

---

### 2. Correlations (`correlations.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /correlations` | View correlation data |
| `GET /correlations/view/{id}` | View specific correlation |
| `GET /correlations/organisations/{id}` | View org correlations |

**Use case**: Track attribute correlations across events, identify related indicators.

---

### 3. Dashboard/Statistics (`stats.py` or `dashboard.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /stats` | Get system statistics |
| `GET /stats/health` | Health check |
| `GET /stats/attributes` | Attribute statistics |
| `GET /stats/events` | Event statistics |
| `GET /stats/users` | User statistics |

**Use case**: Monitor MISP instance health, track threat intel metrics.

---

### 4. Proposals/ShadowAttributes (`proposals.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /shadow_attributes/index` | List proposals |
| `GET /shadow_attributes/view/{id}` | View proposal |
| `POST /shadow_attributes/add/{event_id}` | Add proposal |
| `POST /shadow_attributes/accept/{id}` | Accept proposal |
| `POST /shadow_attributes/discard/{id}` | Discard proposal |
| `POST /shadow_attributes/edit/{id}` | Edit proposal |

**Use case**: Community contribution workflow, propose attribute changes to events.

---

### 5. Audits/Logs (`logs.py` or `audits.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /audit_logs/index` | List audit logs |
| `GET /audit_logs/view/{id}` | View audit entry |
| `GET /admin/audit_logs` | Admin audit logs |

**Use case**: Security compliance, track user actions, investigate incidents.

---

## 🚧 Priority 2: Missing Operations on Existing Commands

### Events (`events.py`) - Add Missing Commands
| Missing Command | Endpoint |
|-----------------|----------|
| `misp events edit` | `POST /events/edit/{id}` |
| `misp events clone` | `POST /events/clone/{id}` |
| `misp events alert` | `GET /events/alert/{id}` |
| `misp events contact` | `GET /events/contact/{id}` |
| `misp events proposal` | `GET /events/proposal/{id}` |

---

### Attributes (`attributes.py`) - Add Missing Commands
| Missing Command | Endpoint |
|-----------------|----------|
| `misp attributes replace` | `POST /attributes/replace/{id}` (bulk replace) |
| `misp attributes attach-to-event` | `POST /attributes/attachToEvent` |

---

### Users (`users.py`) - Add Missing Commands
| Missing Command | Endpoint |
|-----------------|----------|
| `misp users password-reset` | `POST /users/resetPassword/{id}` |
| `misp users key-reset` | `POST /users/resetAuthKey/{id}` |
| `misp users statistics` | `GET /users/statistics/{id}` |

---

### Roles (`roles.py`) - Add Missing Commands
| Missing Command | Endpoint |
|-----------------|----------|
| `misp roles create` | `POST /roles/add` |
| `misp roles edit` | `POST /roles/edit/{id}` |
| `misp roles delete` | `POST /roles/delete/{id}` |

**Current state**: Only `list` and `show` exist.

---

### Noticelists (`noticelists.py`) - Add Missing Commands
| Missing Command | Endpoint |
|-----------------|----------|
| `misp noticelists create` | `POST /noticelists/add` |
| `misp noticelists edit` | `POST /noticelists/edit/{id}` |
| `misp noticelists delete` | `POST /noticelists/delete/{id}` |

**Current state**: Only `list`, `show`, `enabled`, `toggle` exist.

---

## 🔧 Priority 3: Utility Commands

### 6. AuthKeys (`authkeys.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /auth_keys/index` | List API keys |
| `GET /auth_keys/view/{id}` | View API key |
| `POST /auth_keys/add` | Create API key |
| `POST /auth_keys/edit/{id}` | Edit API key |
| `POST /auth_keys/delete/{id}` | Delete API key |

**Use case**: Manage API access credentials.

---

### 7. UserSettings (`usersettings.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /user_settings/index` | List user settings |
| `GET /user_settings/view/{id}` | View setting |
| `POST /user_settings/set` | Set user setting |
| `POST /user_settings/delete/{id}` | Delete setting |

**Use case**: Manage user preferences, UI settings.

---

### 8. Sightings (`sightings.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /sightings/index` | List sightings |
| `POST /sightings/add` | Add sighting |
| `GET /sightings/list/{type}/{id}` | Get sightings for object |
| `POST /sightings/restSearch` | Search sightings |

**Use case**: Track IOC sightings, false positive management.

---

### 9. SightingDB (`sightingdb.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /sightingdb/index` | List sighting DBs |
| `POST /sightingdb/add` | Add sighting DB |
| `POST /sightingdb/sync` | Sync sighting DB |

**Use case**: External sighting database integration.

---

### 10. Brute Force (`bruteforce.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /bruteforce/index` | List blocked IPs |
| `POST /bruteforce/unblock/{id}` | Unblock IP |

**Use case**: Manage brute force protection.

---

### 11. Generic Import (`import.py`)
| Endpoint | Operation |
|----------|-----------|
| `POST /events/import` | Import events |
| `POST /attributes/import` | Import attributes |

**Use case**: Import STIX, STIX2, MISP formats.

---

### 12. Generic Export (`export.py`)
| Endpoint | Operation |
|----------|-----------|
| `GET /events/export/{id}` | Export event |
| `GET /attributes/export` | Export attributes |
| `GET /objects/export` | Export objects |

**Use case**: Export to various formats (JSON, CSV, XML, STIX).

---

## 📊 Coverage Summary

| Category | Current Commands | Missing Commands | Coverage |
|----------|-----------------|-------------------|----------|
| Events | 8 | 4 | 67% |
| Attributes | 7 | 2 | 78% |
| Users | 11 | 3 | 79% |
| Organisations | 0 | 5 | 0% |
| Roles | 2 | 3 | 40% |
| Noticelists | 4 | 3 | 57% |
| Tags | 9 | 2 | 82% |
| Feeds | 11 | 1 | 92% |
| Galaxies | 7 | 2 | 78% |
| Objects | 7 | 1 | 88% |
| Servers | 10 | 2 | 83% |
| Sharing Groups | 8 | 0 | 100% |
| Taxonomies | 7 | 0 | 100% |
| Warninglists | 9 | 0 | 100% |
| Decaying Models | 5 | 0 | 100% |
| News | 5 | 0 | 100% |
| Object Templates | 6 | 0 | 100% |
| Blocklists | 4 | 0 | 100% |
| **New Categories** | **0** | **~50+** | **0%** |

---

## 🎯 Recommended Implementation Order

1. **organisations.py** - Critical for multi-org MISP
2. **events.py** - Add `edit` command (most requested)
3. **roles.py** - Add `create`/`edit` commands
4. **noticelists.py** - Add CRUD commands
5. **proposals.py** - Community workflow
6. **stats.py** - Dashboard/monitoring
7. **authkeys.py** - API key management
8. **logs.py** - Audit trail

---

## 📁 New File Structure

```
src/misp_cli/cli/commands/
├── organisations.py      # NEW
├── correlations.py       # NEW
├── proposals.py          # NEW
├── stats.py              # NEW
├── authkeys.py           # NEW
├── logs.py               # NEW
├── settings.py           # NEW
├── sightings.py          # NEW
├── import.py             # NEW
└── export.py             # NEW
```

Total potential new commands: ~50+ new command variations across 10 new files.

---

*Generated from MISP OpenAPI specification analysis on 2026-02-06*
