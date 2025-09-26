import re
from typing import Dict, Any


EMERGENCY_KEYWORDS = {"accident", "breakdown", "blowout", "emergency", "injured", "help", "medical"}
STATUS_KEYWORDS = {"arrived", "delayed", "driving", "en route", "stuck", "pulling over", "stopped"}


def build_structured_summary(transcript: str) -> Dict[str, Any]:
    text = (transcript or "").lower()

    detected_keywords = sorted({kw for kw in STATUS_KEYWORDS if kw in text})
    emergency_detected = any(kw in text for kw in EMERGENCY_KEYWORDS)

    # noisy environment detection: repeated markers
    noisy_markers = re.findall(r"\b(inaudible|garbled|unclear|can't hear)\b", text)
    noisy_environment = len(noisy_markers) >= 3

    # uncooperative driver detection: many very short utterances (< 3 words)
    segments = [seg.strip() for seg in re.split(r"[.!?\n]+", transcript or "")]
    short_utterance_count = sum(1 for seg in segments if seg and len(seg.split()) < 3)
    uncooperative_driver = short_utterance_count >= 3

    # Enhanced location extraction
    location_patterns = [
        r"near ([a-z0-9 .,'-]+)",
        r"at ([a-z0-9 .,'-]+)",
        r"on ([a-z0-9 .,'-]+)",
        r"mile marker (\d+)",
        r"exit (\d+)",
        r"i-(\d+)",
        r"highway (\d+)",
    ]
    
    location = None
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            location = match.group(1).strip()
            break

    # Enhanced ETA extraction
    eta_patterns = [
        r"eta ([0-9]{1,2})\s*(hour|hours|min|mins|minutes)",
        r"in ([0-9]{1,2})\s*(hour|hours|min|mins|minutes)",
        r"arrive in ([0-9]{1,2})\s*(hour|hours|min|mins|minutes)",
        r"be there in ([0-9]{1,2})\s*(hour|hours|min|mins|minutes)",
        r"tomorrow at ([0-9]{1,2}):?([0-9]{2})?\s*(am|pm)?",
        r"tonight at ([0-9]{1,2}):?([0-9]{2})?\s*(am|pm)?",
    ]
    
    eta_str = None
    for pattern in eta_patterns:
        match = re.search(pattern, text)
        if match:
            if "tomorrow" in pattern or "tonight" in pattern:
                eta_str = f"{match.group(0)}"
            else:
                eta_str = f"{match.group(1)} {match.group(2)}"
            break

    summary: Dict[str, Any] = {
        "keywords": detected_keywords,
        "emergency": emergency_detected,
    }

    # Priority: Emergency > Noisy Environment > Uncooperative Driver > Status Update
    if emergency_detected:
        # Determine emergency type
        emergency_type = "Other"
        if "accident" in text or "crash" in text:
            emergency_type = "Accident"
        elif "breakdown" in text or "blowout" in text or "flat tire" in text:
            emergency_type = "Breakdown"
        elif "medical" in text or "sick" in text or "injured" in text:
            emergency_type = "Medical"
        
        summary.update(
            {
                "call_outcome": "Emergency Detected",
                "emergency_type": emergency_type,
                "emergency_location": location,
                "escalation_status": "Escalation Flagged",
            }
        )
    elif noisy_environment:
        summary.update(
            {
                "call_outcome": "Noisy Environment - Call Ended",
                "noisy_indicator_count": len(noisy_markers),
                "location": location,
            }
        )
    elif uncooperative_driver:
        summary.update(
            {
                "call_outcome": "Uncooperative Driver",
                "short_utterance_count": short_utterance_count,
                "location": location,
            }
        )
    else:
        # Determine call outcome and driver status
        if "arrived" in text or "delivered" in text or "unloading" in text:
            call_outcome = "Arrival Confirmation"
            driver_status = "Arrived"
        elif "delayed" in text or "running late" in text or "behind schedule" in text:
            call_outcome = "In-Transit Update"
            driver_status = "Delayed"
        elif "driving" in text or "en route" in text or "on the way" in text:
            call_outcome = "In-Transit Update"
            driver_status = "Driving"
        elif "stuck" in text or "traffic" in text or "pulling over" in text:
            call_outcome = "In-Transit Update"
            driver_status = "Delayed"
        else:
            call_outcome = "In-Transit Update"
            driver_status = "Unknown"

        summary.update(
            {
                "call_outcome": call_outcome,
                "driver_status": driver_status,
                "current_location": location,
                "eta": eta_str,
            }
        )

    return summary


__all__ = ["build_structured_summary"]


