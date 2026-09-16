"""
keywords.py — CV keyword banks for job scoring.

Each set reflects the skills visible in the corresponding base CV.
The scorer uses the union across all three banks so a single job
can match regardless of which CV would be used.
"""

#Chooses between the domains to identify the type of job and which keywords library to use for scoring.

from unittest import case



SOFTWARE_DOMAIN = {
    'backend', 'frontend', 'fullstack', 'software engineer',
    'software developer'
}

HARDWARE_DOMAIN = {
    'embedded', 'firmware', 'hardware engineer', 'hardware design', 'electronics',
}

IT_DOMAIN = {
    'it analyst', 'data analyst', 'data scientist', 'systems administrator', 'cloud', 'security',
}

#Uses the level of experience libraries to identify the level of the job and assign points to the job score.

#50 points if chosen
KEYWORDS_ENTRY_LEVEL = { 'junior', 'intern', 'entry-level', 'new grad', 'recent graduate', 'recent grad', 
                    'eit', 'e.i.t.', 'engineer-in-training', '0-2 years', '1-3 years', '0-1 years', '0-3 years', '1+ years', '2+ years' }

#25 points if chosen
KEYWORDS_INTERMEDIATE = { 'mid-level', 'intermediate', 'experienced', '3-5 years', '3+ years', '4+ years' }

#0 points if chosen
KEYWORDS_SENIOR = { 'senior', 'lead', 'principal', 'director', 'vp', 'vice president', 'c-level', 'cto', 'ceo', 'cfo', 'cio', '5+ years', '6+ years', '7+ years', '8+ years', '9+ years', '10+ years' }

#Finally adds the keywords from the job description to the list of matched keywords for scoring.

# 42 keywords, 50 potential points
KEYWORDS_SOFTWARE = {
    # Languages
    'python', 'java', 'kotlin', 'javascript', 'typescript',
    'c', 'c++', 'c#',
    # Web / backend
    'rest', 'api', 'graphql', 'microservices',
    'spring', 'node', 'react', 'angular',
    # Data / AI
    'sql', 'nosql', 'mongodb', 'postgresql', 'redis',
    'machine learning', 'deep learning', 'llm',
    # Infra / DevOps
    'docker', 'kubernetes', 'aws', 'azure', 'ci/cd',
    'github actions',
    # Tools
    'git', 'linux', 'unix', 'agile', 'scrum', 'jira', 'ai'
    # Domain'
    'distributed systems', 'real-time', 'embedded linux', 'arm', 'rtos',
}

# 31 keywords, 50 potential points
KEYWORDS_HARDWARE = {
    # HDL / synthesis
    'vhdl', 'verilog', 'systemverilog', 'fpga', 'rtl', 'synthesis',
    'vivado', 'quartus', 'modelsim',
    # Protocols / interfaces
    'gpio', 'i2c', 'uart', 'usb', 'can', 'ethernet',
    # Languages
    'c', 'c++', 'python', 'matlab', 'assembly',
    # Tools / flow
    'altium', 'kicad', 'pcb', 'schematic',
    'oscilloscope', 'logic analyzer',
    # Domain
    'driver', 'bsp', 'bootloader', 'signal processing',
    'rf', 'power electronics',
}

# 39 keywords, 50 potential points
KEYWORDS_IT = {
    # Systems
    'windows', 'active directory', 'group policy', 'intune', 'sccm',
    'linux', 'macos', 'virtualization', 'vmware', 'hyper-v',
    # Cloud / M365
    'azure', 'aws', 'm365', 'office 365', 'sharepoint', 'teams',
    'power automate', 'power platform', 'entra',
    # Networking
    'tcp/ip', 'dns', 'dhcp', 'vpn', 'firewall', 'vlan',
    'networking', 'wireshark', 'cisco',
    # Dev / scripting
    'python', 'powershell', 'bash', 'sql', 'rest api',
    # PM / governance
    'project management', 'pmp', 'project coordinator',
    'documentation', 'stakeholder', 'change management',
}

# 6 keywords, X potential points
KEYWORDS_GENERAL = { 'team player', 'collaborative', 'communication', 'problem solving', 'critical thinking', 'bilingual' }


# Union used by the scorer
ALL_KEYWORDS: set[str] = KEYWORDS_SOFTWARE | KEYWORDS_HARDWARE | KEYWORDS_IT | KEYWORDS_GENERAL

def get_seniority_level(matched: list[str]) -> int:
    """Return the seniority level based on matched keywords."""
    entry_hits = sum(1 for k in matched if k in KEYWORDS_ENTRY_LEVEL)
    intermediate_hits = sum(1 for k in matched if k in KEYWORDS_INTERMEDIATE)
    senior_hits = sum(1 for k in matched if k in KEYWORDS_SENIOR)

    best = max(('ENTRY', entry_hits), ('INTERMEDIATE', intermediate_hits), ('SENIOR', senior_hits), key=lambda x: x[1])

    match best[0]:
        case 'ENTRY':
            return 50
        case 'INTERMEDIATE':
            return 25
        case 'SENIOR':
            return 0
        case _:
            return 0

# Which base CV to suggest based on dominant matched category
def suggest_base(matched: list[str], location: str) -> str:
    """Return the suggested CV base key (e.g. 'SOFT_EN', 'HW_FR', 'IT_EN')."""
    fr = location and any(x in location.lower() for x in ('montreal', 'québec', 'quebec', 'laval', 'longueuil'))
    suffix = '_FR' if fr else '_EN'

    # Step 1

    sw_hits = sum(1 for k in matched if k in SOFTWARE_DOMAIN)
    hw_hits = sum(1 for k in matched if k in HARDWARE_DOMAIN)
    it_hits = sum(1 for k in matched if k in IT_DOMAIN)
    best = max(('SOFT', sw_hits), ('HW', hw_hits), ('IT', it_hits), key=lambda x: x[1])

    #Step 2

    seniority = get_seniority_level(matched)

    # Step 3

    match best[0]:
        case 'SOFT':
            score = sum(3 for k in matched if k in KEYWORDS_SOFTWARE) +  sum(1 for k in matched if k in KEYWORDS_GENERAL) + seniority
        case 'HW':
            score = sum(3 for k in matched if k in KEYWORDS_HARDWARE) +  sum(1 for k in matched if k in KEYWORDS_GENERAL) + seniority
        case 'IT':
            score = sum(3 for k in matched if k in KEYWORDS_IT) +  sum(1 for k in matched if k in KEYWORDS_GENERAL) + seniority

    score = min(100, score) # Cap the score at 100

    return str(score) + '_' + best[0] + suffix
