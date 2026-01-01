"""IDOARRT markdown parsing and validation service."""

import re
from typing import Dict, List, Any, Tuple


class IDOARRTParseError(Exception):
    """Raised when IDOARRT parsing fails."""
    pass


class IDOARRTService:
    """Parse and validate IDOARRT markdown files."""

    REQUIRED_SECTIONS = ["Intent", "Desired Outcomes", "Agenda", "Roles", "Rules", "Time"]

    def parse_idoarrt(self, markdown: str) -> Dict[str, Any]:
        """
        Parse IDOARRT markdown into structured data.

        Args:
            markdown: IDOARRT markdown content

        Returns:
            dict with parsed IDOARRT data

        Raises:
            IDOARRTParseError: If parsing fails or validation errors
        """
        # Split into sections
        sections = self._split_sections(markdown)

        # Validate all required sections exist
        missing_sections = [s for s in self.REQUIRED_SECTIONS if s not in sections]
        if missing_sections:
            raise IDOARRTParseError(f"Missing required sections: {', '.join(missing_sections)}")

        # Parse each section
        try:
            intent = self._parse_intent(sections["Intent"])
            desired_outcomes = self._parse_desired_outcomes(sections["Desired Outcomes"])
            agenda = self._parse_agenda(sections["Agenda"])
            roles = self._parse_roles(sections["Roles"])
            rules = self._parse_rules(sections["Rules"])
            total_duration_minutes = self._parse_time(sections["Time"])
        except Exception as e:
            raise IDOARRTParseError(f"Parsing error: {str(e)}")

        # Validate agenda time allocations
        agenda_total = sum(item["duration_minutes"] for item in agenda)
        if agenda_total != total_duration_minutes:
            raise IDOARRTParseError(
                f"Agenda times ({agenda_total} min) don't match total time ({total_duration_minutes} min)"
            )

        return {
            "intent": intent,
            "desired_outcomes": desired_outcomes,
            "agenda": agenda,
            "roles": roles,
            "rules": rules,
            "total_duration_minutes": total_duration_minutes,
        }

    def _split_sections(self, markdown: str) -> Dict[str, str]:
        """Split markdown into sections based on # headers."""
        sections: Dict[str, str] = {}
        current_section: str | None = None
        current_content: List[str] = []

        for line in markdown.split("\n"):
            # Check if line is a header
            header_match = re.match(r"^#\s+(.+)$", line.strip())
            if header_match:
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = header_match.group(1)
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _parse_intent(self, content: str) -> str:
        """Parse Intent section."""
        intent = content.strip()
        if not intent:
            raise IDOARRTParseError("Intent cannot be empty")
        return intent

    def _parse_desired_outcomes(self, content: str) -> List[str]:
        """Parse Desired Outcomes section (bullet list)."""
        outcomes = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                outcome = line[1:].strip()
                if outcome:
                    outcomes.append(outcome)

        if not outcomes:
            raise IDOARRTParseError("Desired Outcomes must have at least one item")

        return outcomes

    def _parse_agenda(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse Agenda section (numbered list with time allocations).

        Expected format:
        1. Topic name (15 min)
        2. Another topic (20 min)
        """
        agenda = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Match numbered list with time: "1. Topic (15 min)"
            match = re.match(r"^\d+\.\s+(.+?)\s*\((\d+)\s*min\)$", line, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                duration = int(match.group(2))
                agenda.append({
                    "topic": topic,
                    "duration_minutes": duration,
                })
            else:
                # Try without "min" suffix: "1. Topic (15)"
                match = re.match(r"^\d+\.\s+(.+?)\s*\((\d+)\)$", line)
                if match:
                    topic = match.group(1).strip()
                    duration = int(match.group(2))
                    agenda.append({
                        "topic": topic,
                        "duration_minutes": duration,
                    })
                elif re.match(r"^\d+\.", line):
                    # Numbered item without time allocation
                    raise IDOARRTParseError(
                        f"Agenda item missing time allocation: {line}"
                    )

        if not agenda:
            raise IDOARRTParseError("Agenda must have at least one item")

        return agenda

    def _parse_roles(self, content: str) -> Dict[str, str]:
        """
        Parse Roles section (bullet list with role: person).

        Expected format:
        - Facilitator: Anna
        - Timekeeper: Björn
        """
        roles = {}
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                # Remove bullet
                line = line[1:].strip()
                # Split by colon
                if ":" in line:
                    role, person = line.split(":", 1)
                    roles[role.strip()] = person.strip()

        if not roles:
            raise IDOARRTParseError("Roles must have at least one role defined")

        return roles

    def _parse_rules(self, content: str) -> List[str]:
        """Parse Rules section (bullet list)."""
        rules = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                rule = line[1:].strip()
                if rule:
                    rules.append(rule)

        if not rules:
            raise IDOARRTParseError("Rules must have at least one rule")

        return rules

    def _parse_time(self, content: str) -> int:
        """
        Parse Time section.

        Expected format:
        Total: 60 minutes
        """
        # Match "Total: XX minutes" or "Total: XX min"
        match = re.search(r"Total:\s*(\d+)\s*(?:minutes?|min)?", content, re.IGNORECASE)
        if match:
            total = int(match.group(1))
            if total <= 0:
                raise IDOARRTParseError("Total time must be positive")
            return total

        raise IDOARRTParseError("Time section must contain 'Total: XX minutes'")

    def validate_idoarrt(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validate parsed IDOARRT data and return list of validation errors.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Intent validation
        if not parsed_data.get("intent"):
            errors.append("Intent is required")

        # Desired Outcomes validation
        if not parsed_data.get("desired_outcomes"):
            errors.append("At least one Desired Outcome is required")

        # Agenda validation
        agenda = parsed_data.get("agenda", [])
        if not agenda:
            errors.append("At least one Agenda item is required")
        else:
            # Check time allocations
            total_time = parsed_data.get("total_duration_minutes", 0)
            agenda_total = sum(item["duration_minutes"] for item in agenda)
            if agenda_total != total_time:
                errors.append(
                    f"Agenda times ({agenda_total} min) don't match total time ({total_time} min)"
                )

        # Roles validation
        if not parsed_data.get("roles"):
            errors.append("At least one Role is required")

        # Rules validation
        if not parsed_data.get("rules"):
            errors.append("At least one Rule is required")

        # Time validation
        if not parsed_data.get("total_duration_minutes") or parsed_data["total_duration_minutes"] <= 0:
            errors.append("Total time must be positive")

        return errors
