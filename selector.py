import questionary
import sys
import os

def get_selection():
    choices = [
        questionary.Choice("--- ALL SERVICES ---", value="ALL"),
        questionary.Choice("LFI/RCE (Apache 2.4.49)", value="lfi-target"),
        questionary.Choice("RCE (Atom CMS 2.0)", value="rce-target target-db"),
        questionary.Choice("SQLi (Cuppa CMS v1.0)", value="sqli-target target-db"),
        questionary.Choice("XSS (WonderCMS 3.4.2)", value="xss-target"),
        questionary.Choice("PHP RCE (Backdoor)", value="backdoor-target"),
        questionary.Choice("SSRF (osTicket 1.14.2)", value="ssrf-target target-db"),
        questionary.Choice("Auth Failure (Fuel CMS 1.4.1)", value="auth-target target-db"),
        questionary.Choice("Insecure Design (Bus Pass 1.0)", value="design-target target-db"),
        questionary.Choice("Security Misconfig (CMSimple 5.15)", value="config-target"),
        questionary.Choice("Cryptographic Failure (SweetRice 1.5.1)", value="crypto-target"),
        questionary.Choice("Outdated Components (Log4j / Log4Shell)", value="outdated-target"),
    ]

    selected = questionary.checkbox(
        "Select VulnHive nodes to spin up (Space to select, Enter to start):",
        choices=choices
    ).ask()

    if not selected:
        if os.path.exists(".selection"):
            os.remove(".selection")
        sys.exit(0)

    # Handle "ALL SERVICES" shortcut
    if "ALL" in selected:
        # Get all values except "ALL" itself
        all_services = [c.value for c in choices if c.value != "ALL"]
        selection = " ".join(all_services)
    else:
        selection = " ".join(selected)

    # Flatten duplicates like target-db
    unique_selection = " ".join(set(selection.split()))
    
    with open(".selection", "w") as f:
        f.write(unique_selection)

if __name__ == "__main__":
    get_selection()
