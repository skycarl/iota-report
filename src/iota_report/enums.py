"""Controlled vocabularies for the portable occultation report.

Every enum is a ``(str, Enum)`` whose *value* is a stable, JSON-friendly token.
The original Excel display strings are preserved in the ``LABELS`` map for UI use
(dropdown labels), so producers can render human text without hard-coding it.

Vocabularies are taken verbatim from the IOTA North America report form analysis
(``features/report-overhaul/excel-form-analysis.md`` §3).
"""

from __future__ import annotations

from enum import Enum


class ObservationResult(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    UNSURE = "UNSURE"


class StarCatalog(str, Enum):
    """Star catalog identifiers.

    Values are identical to iota-hub's ``StarCatalog``
    (``apps/api/app/models/api/common.py``) so the hub mapping is identity.
    """

    TYC = "TYC"
    HIP = "HIP"
    UCAC2 = "UCAC2"
    UCAC3 = "UCAC3"
    UCAC4 = "UCAC4"
    G_COORDS = "G_COORDS"
    URAT1 = "URAT1"
    B1 = "1B"
    N1 = "1N"


class Datum(str, Enum):
    NAD1927 = "NAD1927"
    WGS84 = "WGS84"
    EP1950 = "EP1950"
    TOKYO = "TOKYO"
    GBSN80 = "GBSN80"
    OTHER = "OTHER"


class TelescopeType(str, Enum):
    NEWTONIAN = "NEWTONIAN"
    SCT = "SCT"
    REFRACTOR = "REFRACTOR"
    DOBSONIAN = "DOBSONIAN"
    BINOCULARS = "BINOCULARS"
    NO_OPTICAL_AID = "NO_OPTICAL_AID"
    OTHER = "OTHER"


class TimeSource(str, Enum):
    GPS_TIME_INSERTED = "GPS_TIME_INSERTED"
    GPS_OTHER_LINKING = "GPS_OTHER_LINKING"
    VIDEO_AUDIO_TIME_SIGNAL = "VIDEO_AUDIO_TIME_SIGNAL"
    TAPE_RECORDER_TIME_SIGNAL = "TAPE_RECORDER_TIME_SIGNAL"
    EYE_EAR_TIME_SIGNAL = "EYE_EAR_TIME_SIGNAL"
    STOPWATCH = "STOPWATCH"
    RADIO_BROADCAST_CALIBRATED = "RADIO_BROADCAST_CALIBRATED"
    OTHER = "OTHER"


class TimingMethod(str, Enum):
    VISUAL_PE_APPLIED = "VISUAL_PE_APPLIED"
    VISUAL_STANDARD_PE_APPLIED = "VISUAL_STANDARD_PE_APPLIED"
    VISUAL_NO_PE_APPLIED = "VISUAL_NO_PE_APPLIED"
    VIDEO_FRAME_ANALYSIS = "VIDEO_FRAME_ANALYSIS"
    VIDEO_PHOTO_PHOTOELECTRIC = "VIDEO_PHOTO_PHOTOELECTRIC"
    DURATION_ONLY = "DURATION_ONLY"
    DRIFT_SCAN = "DRIFT_SCAN"
    PRELIMINARY_ONLY = "PRELIMINARY_ONLY"


class TimingDevice(str, Enum):
    ADVS = "ADVS"
    AFT_OFT_FLASH_TAG = "AFT_OFT_FLASH_TAG"
    ASTRID = "ASTRID"
    BEEPERBOX = "BEEPERBOX"
    CELLPHONE = "CELLPHONE"
    COMPUTER_NTP = "COMPUTER_NTP"
    GPS = "GPS"
    GPS_ABC = "GPS_ABC"
    IOTA_VTI = "IOTA_VTI"
    KIWI_OSD = "KIWI_OSD"
    STOPWATCH = "STOPWATCH"
    WWV_RADIO = "WWV_RADIO"
    OTHER = "OTHER"


class OteProgram(str, Enum):
    NONE = "NONE"  # Excel blank
    MANUAL = "MANUAL"
    AOTA_WITH_CAMDELAY = "AOTA_WITH_CAMDELAY"
    OCCULAR = "OCCULAR"
    R_OTE_WITH_CAMDELAY = "R_OTE_WITH_CAMDELAY"
    R_OTE_WITHOUT_CAMDELAY = "R_OTE_WITHOUT_CAMDELAY"
    PYOTE = "PYOTE"
    OTHER = "OTHER"


class CameraModel(str, Enum):
    CCD_DRIFT_SCAN = "CCD_DRIFT_SCAN"
    ASTRID = "ASTRID"
    FLEA3_03S1_ADVS = "FLEA3_03S1_ADVS"
    FLEA3_03S3_ADVS = "FLEA3_03S3_ADVS"
    FLEA3_28S4M_ADVS = "FLEA3_28S4M_ADVS"
    GRASSHOPPER_EXPRESS_ADVS = "GRASSHOPPER_EXPRESS_ADVS"
    G_STAR = "G_STAR"
    KPC_350BH = "KPC_350BH"
    LN_300_11673 = "LN_300_11673"
    MALLINCAM = "MALLINCAM"
    MINTRON_12V1C_EX = "MINTRON_12V1C_EX"
    PC164C = "PC164C"
    PC164C_EX = "PC164C_EX"
    PC165_DNR = "PC165_DNR"
    PHOTOMETER = "PHOTOMETER"
    QHY_174_GPS = "QHY_174_GPS"
    RUNCAM_NIGHT_EAGLE = "RUNCAM_NIGHT_EAGLE"
    RUNCAM_NIGHT_EAGLE_ASTRO = "RUNCAM_NIGHT_EAGLE_ASTRO"
    SAMSUNG_SBC_2000 = "SAMSUNG_SBC_2000"
    VISUAL = "VISUAL"
    WATEC_120N = "WATEC_120N"
    WATEC_120N_PLUS = "WATEC_120N_PLUS"
    WATEC_902H = "WATEC_902H"
    WATEC_910BD = "WATEC_910BD"
    WATEC_910HX = "WATEC_910HX"
    OTHER = "OTHER"


class VideoFormat(str, Enum):
    AAV_NTSC = "AAV_NTSC"
    AAV_PAL = "AAV_PAL"
    ADVS = "ADVS"
    CCD_DRIFT = "CCD_DRIFT"
    FITS_IMAGES = "FITS_IMAGES"
    NTSC_EIA = "NTSC_EIA"
    PAL_CCIR = "PAL_CCIR"


class ExposureSetting(str, Enum):
    OTHER = "OTHER"
    X1 = "X1"
    X2 = "X2"
    X4 = "X4"
    X6 = "X6"
    X8 = "X8"
    X10 = "X10"
    X12 = "X12"
    X14 = "X14"
    X16 = "X16"
    X24 = "X24"
    X32 = "X32"
    X48 = "X48"
    X64 = "X64"
    X96 = "X96"
    X128 = "X128"
    X256 = "X256"
    X512 = "X512"


class NightShutter(str, Enum):
    NS1 = "NS1"
    NS2 = "NS2"
    NS3 = "NS3"


class CloudCondition(str, Enum):
    CLEAR = "CLEAR"
    FOG = "FOG"
    THIN_CLOUD = "THIN_CLOUD"
    THICK_CLOUD = "THICK_CLOUD"
    BROKEN_CLOUD = "BROKEN_CLOUD"
    STAR_FAINT = "STAR_FAINT"
    AVERTED_VISION = "AVERTED_VISION"


class Stability(str, Enum):
    STEADY = "STEADY"
    SLIGHT_FLICKERING = "SLIGHT_FLICKERING"
    STRONG_FLICKERING = "STRONG_FLICKERING"


class YesNoMaybe(str, Enum):
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"


class TimingMode(str, Enum):
    AUTO_CORRECTED = "AUTO_CORRECTED"
    MANUALLY_CORRECTED = "MANUALLY_CORRECTED"


class PassDirection(str, Enum):
    N = "N"
    S = "S"
    E = "E"
    W = "W"


# --- Human-readable labels (original Excel display strings) --------------------
# Keyed by enum member; consumed by producing UIs to render dropdown text without
# hard-coding it. Not part of the wire format.

LABELS: dict[Enum, str] = {
    ObservationResult.POSITIVE: "Positive",
    ObservationResult.NEGATIVE: "Negative",
    ObservationResult.UNSURE: "Unsure",
    StarCatalog.TYC: "TYC (Tycho)",
    StarCatalog.HIP: "HIP (Hipparcos)",
    StarCatalog.UCAC2: "UCAC2",
    StarCatalog.UCAC3: "UCAC3",
    StarCatalog.UCAC4: "UCAC4",
    StarCatalog.G_COORDS: "G-coords",
    StarCatalog.URAT1: "URAT1",
    StarCatalog.B1: "USNO-B1 (1B)",
    StarCatalog.N1: "NOMAD/USNO-N1 (1N)",
    Datum.NAD1927: "NAD1927",
    Datum.WGS84: "WGS84",
    Datum.EP1950: "EP1950",
    Datum.TOKYO: "Tokyo",
    Datum.GBSN80: "GBSN80",
    Datum.OTHER: "Other",
    TelescopeType.NEWTONIAN: "Newtonian",
    TelescopeType.SCT: "SCT including Cass and Mak",
    TelescopeType.REFRACTOR: "Refractor",
    TelescopeType.DOBSONIAN: "Dobsonian",
    TelescopeType.BINOCULARS: "binoculars",
    TelescopeType.NO_OPTICAL_AID: "no optical aid",
    TelescopeType.OTHER: "other - specify below",
    TimeSource.GPS_TIME_INSERTED: "GPS - time inserted",
    TimeSource.GPS_OTHER_LINKING: "GPS - other linking",
    TimeSource.VIDEO_AUDIO_TIME_SIGNAL: "Video + audio time signal",
    TimeSource.TAPE_RECORDER_TIME_SIGNAL: "Tape Recorder + time signal",
    TimeSource.EYE_EAR_TIME_SIGNAL: "Eye-Ear + time signal",
    TimeSource.STOPWATCH: "Stopwatch",
    TimeSource.RADIO_BROADCAST_CALIBRATED: "Radio broadcast - calibrated",
    TimeSource.OTHER: "other",
    TimingMethod.VISUAL_PE_APPLIED: "Visual, PE applied",
    TimingMethod.VISUAL_STANDARD_PE_APPLIED: "Visual, standard PE applied",
    TimingMethod.VISUAL_NO_PE_APPLIED: "Visual, no PE applied",
    TimingMethod.VIDEO_FRAME_ANALYSIS: "Video with frame analysis",
    TimingMethod.VIDEO_PHOTO_PHOTOELECTRIC: "Video, photo or photoelectric",
    TimingMethod.DURATION_ONLY: "Only duration timed",
    TimingMethod.DRIFT_SCAN: "Drift scan",
    TimingMethod.PRELIMINARY_ONLY: "Preliminary only",
    TimingDevice.ADVS: "ADVS",
    TimingDevice.AFT_OFT_FLASH_TAG: "AFT or OFT Flash Tag",
    TimingDevice.ASTRID: "ASTRID",
    TimingDevice.BEEPERBOX: "Beeperbox",
    TimingDevice.CELLPHONE: "Cellphone",
    TimingDevice.COMPUTER_NTP: "Computer NTP",
    TimingDevice.GPS: "GPS",
    TimingDevice.GPS_ABC: "GPS-ABC",
    TimingDevice.IOTA_VTI: "IOTA-VTI",
    TimingDevice.KIWI_OSD: "KIWI-OSD",
    TimingDevice.STOPWATCH: "Stopwatch",
    TimingDevice.WWV_RADIO: "WWV Radio Time",
    TimingDevice.OTHER: "Other - Specify in Comments",
    OteProgram.NONE: "(blank)",
    OteProgram.MANUAL: "Manual",
    OteProgram.AOTA_WITH_CAMDELAY: "AOTA w/ CamDelay Corrections",
    OteProgram.OCCULAR: "Occular",
    OteProgram.R_OTE_WITH_CAMDELAY: "R-OTE w/ CamDelay Corrections",
    OteProgram.R_OTE_WITHOUT_CAMDELAY: "R-OTE w/o CamDelay Corrections",
    OteProgram.PYOTE: "PYOTE",
    OteProgram.OTHER: "Other - Specify in Comments",
    CameraModel.CCD_DRIFT_SCAN: "CCD Drift Scan",
    CameraModel.ASTRID: "ASTRID",
    CameraModel.FLEA3_03S1_ADVS: "Flea 3-03S1 with ADVS",
    CameraModel.FLEA3_03S3_ADVS: "Flea 3-03S3 with ADVS",
    CameraModel.FLEA3_28S4M_ADVS: "Flea 3-28S4M with ADVS",
    CameraModel.GRASSHOPPER_EXPRESS_ADVS: "Grasshopper Express with ADVS",
    CameraModel.G_STAR: "G-Star",
    CameraModel.KPC_350BH: "KPC-350BH",
    CameraModel.LN_300_11673: "LN-300-11673",
    CameraModel.MALLINCAM: "Mallincam",
    CameraModel.MINTRON_12V1C_EX: "Mintron 12v1C-EX",
    CameraModel.PC164C: "PC164C",
    CameraModel.PC164C_EX: "PC164C-EX",
    CameraModel.PC165_DNR: "PC165-DNR",
    CameraModel.PHOTOMETER: "Photometer",
    CameraModel.QHY_174_GPS: "QHY 174 GPS",
    CameraModel.RUNCAM_NIGHT_EAGLE: "RunCam Night Eagle",
    CameraModel.RUNCAM_NIGHT_EAGLE_ASTRO: "RunCam Night Eagle Astro",
    CameraModel.SAMSUNG_SBC_2000: "Samsung SBC-2000",
    CameraModel.VISUAL: "Visual",
    CameraModel.WATEC_120N: "Watec 120N",
    CameraModel.WATEC_120N_PLUS: "Watec 120N+",
    CameraModel.WATEC_902H: "Watec 902H",
    CameraModel.WATEC_910BD: "Watec 910BD",
    CameraModel.WATEC_910HX: "Watec 910HX",
    CameraModel.OTHER: "Other - List in Comments",
    VideoFormat.AAV_NTSC: "AAV-NTSC",
    VideoFormat.AAV_PAL: "AAV-PAL",
    VideoFormat.ADVS: "ADVS",
    VideoFormat.CCD_DRIFT: "CCD Drift",
    VideoFormat.FITS_IMAGES: "FITS Images",
    VideoFormat.NTSC_EIA: "NTSC/EIA",
    VideoFormat.PAL_CCIR: "PAL/CCIR",
    ExposureSetting.OTHER: "Other",
    ExposureSetting.X1: "1x",
    ExposureSetting.X2: "2x",
    ExposureSetting.X4: "4x",
    ExposureSetting.X6: "6x",
    ExposureSetting.X8: "8x",
    ExposureSetting.X10: "10x",
    ExposureSetting.X12: "12x",
    ExposureSetting.X14: "14x",
    ExposureSetting.X16: "16x",
    ExposureSetting.X24: "24x",
    ExposureSetting.X32: "32x",
    ExposureSetting.X48: "48x",
    ExposureSetting.X64: "64x",
    ExposureSetting.X96: "96x",
    ExposureSetting.X128: "128x",
    ExposureSetting.X256: "256x",
    ExposureSetting.X512: "512x",
    NightShutter.NS1: "NS1",
    NightShutter.NS2: "NS2",
    NightShutter.NS3: "NS3",
    CloudCondition.CLEAR: "Clear",
    CloudCondition.FOG: "Fog",
    CloudCondition.THIN_CLOUD: "Thin cloud < 2",
    CloudCondition.THICK_CLOUD: "Thick cloud > 2",
    CloudCondition.BROKEN_CLOUD: "Broken cloud",
    CloudCondition.STAR_FAINT: "Star faint",
    CloudCondition.AVERTED_VISION: "Averted vision",
    Stability.STEADY: "Steady",
    Stability.SLIGHT_FLICKERING: "Slight flickering",
    Stability.STRONG_FLICKERING: "Strong flickering",
    YesNoMaybe.YES: "yes",
    YesNoMaybe.NO: "no",
    YesNoMaybe.MAYBE: "maybe",
    TimingMode.AUTO_CORRECTED: "Auto-corrected (enter raw VTI times)",
    TimingMode.MANUALLY_CORRECTED: "Manually corrected (enter final times)",
    PassDirection.N: "N",
    PassDirection.S: "S",
    PassDirection.E: "E",
    PassDirection.W: "W",
}
