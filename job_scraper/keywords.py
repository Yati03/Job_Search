"""
keywords.py — CV keyword banks for job scoring.

Each set reflects the skills visible in the corresponding base CV.
The scorer uses the union across all three banks so a single job
can match regardless of which CV would be used.
"""

# 47 keywords, 50 potential points
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
    # Domain
    'backend', 'frontend', 'fullstack', 'software engineer',
    'software developer', 'distributed systems', 'real-time',
    'embedded linux', 'arm', 'rtos',
}

# 36 keywords, 50 potential points
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
    'embedded', 'firmware', 'driver', 'bsp', 'bootloader',
    'hardware engineer', 'hardware design', 'signal processing',
    'rf', 'power electronics',
}

# 45 keywords, 50 potential points
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
    # Domain
    'it analyst', 'data analyst', 'data scientist', 'systems administrator', 'cloud', 'security',
}

#10 keywords, 50 potential points

KEYWORDS_GENERAL = { 'bilingual', 'junior', 'intern', 'entry-level', 'new grad', 'recent graduate', 'recent grad', 
                    'eit', 'e.i.t.', 'engineer-in-training'}


# Union used by the scorer
ALL_KEYWORDS: set[str] = KEYWORDS_SOFTWARE | KEYWORDS_HARDWARE | KEYWORDS_IT | KEYWORDS_GENERAL

# Which base CV to suggest based on dominant matched category
def suggest_base(matched: list[str], location: str) -> str:
    """Return the suggested CV base key (e.g. 'SOFT_EN', 'HW_FR', 'IT_EN')."""
    fr = location and any(x in location.lower() for x in ('montreal', 'québec', 'quebec', 'laval', 'longueuil'))
    suffix = '_FR' if fr else '_EN'

    gen_hits = sum(5.0 for k in matched if k in KEYWORDS_GENERAL)
    sw_hits = sum(1.06 for k in matched if k in KEYWORDS_SOFTWARE) + gen_hits
    hw_hits = sum(1.38 for k in matched if k in KEYWORDS_HARDWARE) + gen_hits
    it_hits = sum(1.11 for k in matched if k in KEYWORDS_IT) + gen_hits

    best = max(('SOFT', sw_hits), ('HW', hw_hits), ('IT', it_hits), key=lambda x: x[1])
    return best[0] + suffix
