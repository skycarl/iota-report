/**
 * A complete, portable occultation observation report.
 */
export interface IotaReport {
    camera:    CameraSetup;
    comments?: null | string;
    /**
     * Producing app + version, e.g. 'iota-hub/2026.07'
     */
    created_with?:   null | string;
    environment:     Environment;
    event:           EventIdentity;
    miss?:           MissDetails | null;
    observer:        Observer;
    result:          ObservationResult;
    schema_version?: string;
    station:         Station;
    telescope:       Telescope;
    timing_setup:    TimingSetup;
    timings:         EventTimings;
}

export interface CameraSetup {
    camera_model: CameraModel;
    /**
     * Required when camera_model == OTHER
     */
    camera_other?: null | string;
    /**
     * Filter type / special settings
     */
    detector_notes?: null | string;
    /**
     * Integration length in FIELDS
     */
    exposure: ExposureSetting;
    /**
     * Required for RUNCAM_NIGHT_EAGLE_ASTRO in AUTO_CORRECTED mode
     */
    rolling_shutter?: RollingShutterInputs | null;
    video_format:     VideoFormat;
}

export enum CameraModel {
    Astrid = "ASTRID",
    CcdDriftScan = "CCD_DRIFT_SCAN",
    Flea303S1Advs = "FLEA3_03S1_ADVS",
    Flea303S3Advs = "FLEA3_03S3_ADVS",
    Flea328S4MAdvs = "FLEA3_28S4M_ADVS",
    GStar = "G_STAR",
    GrasshopperExpressAdvs = "GRASSHOPPER_EXPRESS_ADVS",
    Kpc350Bh = "KPC_350BH",
    Ln300_11673 = "LN_300_11673",
    Mallincam = "MALLINCAM",
    Mintron12V1CEx = "MINTRON_12V1C_EX",
    Other = "OTHER",
    Pc164C = "PC164C",
    Pc164CEx = "PC164C_EX",
    Pc165Dnr = "PC165_DNR",
    Photometer = "PHOTOMETER",
    Qhy174_Gps = "QHY_174_GPS",
    RuncamNightEagle = "RUNCAM_NIGHT_EAGLE",
    RuncamNightEagleAstro = "RUNCAM_NIGHT_EAGLE_ASTRO",
    SamsungSbc2000 = "SAMSUNG_SBC_2000",
    Visual = "VISUAL",
    Watec120N = "WATEC_120N",
    Watec120NPlus = "WATEC_120N_PLUS",
    Watec902H = "WATEC_902H",
    Watec910Bd = "WATEC_910BD",
    Watec910Hx = "WATEC_910HX",
}

/**
 * Integration length in FIELDS
 */
export enum ExposureSetting {
    Other = "OTHER",
    X1 = "X1",
    X10 = "X10",
    X12 = "X12",
    X128 = "X128",
    X14 = "X14",
    X16 = "X16",
    X2 = "X2",
    X24 = "X24",
    X256 = "X256",
    X32 = "X32",
    X4 = "X4",
    X48 = "X48",
    X512 = "X512",
    X6 = "X6",
    X64 = "X64",
    X8 = "X8",
    X96 = "X96",
}

export interface RollingShutterInputs {
    night_shutter: NightShutter;
    /**
     * Star Y-pixel at D (per-format max enforced by engine)
     */
    star_y_at_d: number;
    /**
     * Star Y-pixel at R
     */
    star_y_at_r: number;
}

export enum NightShutter {
    Ns1 = "NS1",
    Ns2 = "NS2",
    Ns3 = "NS3",
}

export enum VideoFormat {
    AavNtsc = "AAV_NTSC",
    AavPal = "AAV_PAL",
    Advs = "ADVS",
    CcdDrift = "CCD_DRIFT",
    FitsImages = "FITS_IMAGES",
    NtscEia = "NTSC_EIA",
    PalCcir = "PAL_CCIR",
}

export interface Environment {
    interruptions?:    ObservingInterruption[];
    other_conditions?: null | string;
    stability:         Stability;
    temperature_c?:    number | null;
    transparency:      CloudCondition;
}

export interface ObservingInterruption {
    end_utc:   Date;
    reason?:   null | string;
    start_utc: Date;
}

export enum Stability {
    SlightFlickering = "SLIGHT_FLICKERING",
    Steady = "STEADY",
    StrongFlickering = "STRONG_FLICKERING",
}

export enum CloudCondition {
    AvertedVision = "AVERTED_VISION",
    BrokenCloud = "BROKEN_CLOUD",
    Clear = "CLEAR",
    Fog = "FOG",
    StarFaint = "STAR_FAINT",
    ThickCloud = "THICK_CLOUD",
    ThinCloud = "THIN_CLOUD",
}

export interface EventIdentity {
    asteroid_name: string;
    /**
     * Minor-planet number; None for unnumbered objects
     */
    asteroid_number?:          number | null;
    is_lucky_star_or_rio_tno?: boolean;
    predicted_time_utc:        Date;
    /**
     * Occult-XML compatibility, e.g. '2014 MU69'
     */
    provisional_designation?: null | string;
    second_star?:             YesNoMaybe | null;
    star_catalog:             StarCatalog;
    /**
     * Catalog-specific format, dashes preserved (e.g. '1234-56789-1')
     */
    star_number: string;
}

export enum YesNoMaybe {
    Maybe = "MAYBE",
    No = "NO",
    Yes = "YES",
}

/**
 * Star catalog identifiers.
 *
 * Values are identical to iota-hub's ``StarCatalog``
 * (``apps/api/app/models/api/common.py``) so the hub mapping is identity.
 */
export enum StarCatalog {
    GCoords = "G_COORDS",
    Hip = "HIP",
    The1B = "1B",
    The1N = "1N",
    Tyc = "TYC",
    Ucac2 = "UCAC2",
    Ucac3 = "UCAC3",
    Ucac4 = "UCAC4",
    Urat1 = "URAT1",
}

export interface MissDetails {
    closest_approach_arcsec?: number | null;
    pass_direction?:          PassDirection | null;
    was_miss:                 YesNoMaybe;
}

export enum PassDirection {
    E = "E",
    N = "N",
    S = "S",
    W = "W",
}

export interface Observer {
    email: string;
    /**
     * City, State, Country (free text)
     */
    home_location:    string;
    mailing_address?: null | string;
    names:            string[];
    phone?:           null | string;
}

export enum ObservationResult {
    Negative = "NEGATIVE",
    Positive = "POSITIVE",
    Unsure = "UNSURE",
}

export interface Station {
    datum?: Datum;
    /**
     * Metres above MSL
     */
    elevation_m: number;
    /**
     * Signed decimal degrees; South negative
     */
    latitude_deg: number;
    /**
     * Nearest town + state/province + 2-letter country code
     */
    location_name: string;
    /**
     * East positive, West negative
     */
    longitude_deg: number;
}

export enum Datum {
    Ep1950 = "EP1950",
    Gbsn80 = "GBSN80",
    Nad1927 = "NAD1927",
    Other = "OTHER",
    Tokyo = "TOKYO",
    Wgs84 = "WGS84",
}

export interface Telescope {
    aperture_cm: number;
    focal_ratio: number;
    /**
     * Visual observations only
     */
    magnification?: number | null;
    /**
     * 'other - specify' free text
     */
    notes?:         null | string;
    telescope_type: TelescopeType;
}

export enum TelescopeType {
    Binoculars = "BINOCULARS",
    Dobsonian = "DOBSONIAN",
    Newtonian = "NEWTONIAN",
    NoOpticalAid = "NO_OPTICAL_AID",
    Other = "OTHER",
    Refractor = "REFRACTOR",
    Sct = "SCT",
}

export interface TimingSetup {
    /**
     * Asteroid visible before/during occultation (small mag-drop events)
     */
    asteroid_visible: boolean;
    method:           TimingMethod;
    /**
     * Governs corrections; NONE == Excel's blank OTE
     */
    ote_program: OteProgram;
    time_source: TimeSource;
    /**
     * The VTI (video time inserter)
     */
    timing_device: TimingDevice;
}

export enum TimingMethod {
    DriftScan = "DRIFT_SCAN",
    DurationOnly = "DURATION_ONLY",
    PreliminaryOnly = "PRELIMINARY_ONLY",
    VideoFrameAnalysis = "VIDEO_FRAME_ANALYSIS",
    VideoPhotoPhotoelectric = "VIDEO_PHOTO_PHOTOELECTRIC",
    VisualNoPEApplied = "VISUAL_NO_PE_APPLIED",
    VisualPEApplied = "VISUAL_PE_APPLIED",
    VisualStandardPEApplied = "VISUAL_STANDARD_PE_APPLIED",
}

/**
 * Governs corrections; NONE == Excel's blank OTE
 */
export enum OteProgram {
    AotaWithCamdelay = "AOTA_WITH_CAMDELAY",
    Manual = "MANUAL",
    None = "NONE",
    Occular = "OCCULAR",
    Other = "OTHER",
    Pyote = "PYOTE",
    ROteWithCamdelay = "R_OTE_WITH_CAMDELAY",
    ROteWithoutCamdelay = "R_OTE_WITHOUT_CAMDELAY",
}

export enum TimeSource {
    EyeEarTimeSignal = "EYE_EAR_TIME_SIGNAL",
    GpsOtherLinking = "GPS_OTHER_LINKING",
    GpsTimeInserted = "GPS_TIME_INSERTED",
    Other = "OTHER",
    RadioBroadcastCalibrated = "RADIO_BROADCAST_CALIBRATED",
    Stopwatch = "STOPWATCH",
    TapeRecorderTimeSignal = "TAPE_RECORDER_TIME_SIGNAL",
    VideoAudioTimeSignal = "VIDEO_AUDIO_TIME_SIGNAL",
}

/**
 * The VTI (video time inserter)
 */
export enum TimingDevice {
    Advs = "ADVS",
    AftOftFlashTag = "AFT_OFT_FLASH_TAG",
    Astrid = "ASTRID",
    Beeperbox = "BEEPERBOX",
    Cellphone = "CELLPHONE",
    ComputerNTP = "COMPUTER_NTP",
    Gps = "GPS",
    GpsAbc = "GPS_ABC",
    IotaVti = "IOTA_VTI",
    KiwiOsd = "KIWI_OSD",
    Other = "OTHER",
    Stopwatch = "STOPWATCH",
    WwvRadio = "WWV_RADIO",
}

export interface EventTimings {
    /**
     * Populated by apply_corrections(); None until computed
     */
    corrected?:          CorrectedTimings | null;
    disappearance?:      TimingMeasurement | null;
    reappearance?:       TimingMeasurement | null;
    signal_to_noise?:    number | null;
    start_observing_utc: Date;
    stop_observing_utc:  Date;
    timing_mode:         TimingMode;
}

/**
 * Computed correction block, embedded so the report is self-contained.
 */
export interface CorrectedTimings {
    camera_delay_d_s?:  number;
    camera_delay_r_s?:  number;
    disappearance_utc?: Date | null;
    /**
     * Raw time within |correction| + 2s of 00:00:00 UT — review flag only
     */
    near_midnight_review?: boolean;
    reappearance_utc?:     Date | null;
    total_correction_d_s?: number;
    total_correction_r_s?: number;
    vti_offset_d_s?:       number;
    vti_offset_r_s?:       number;
}

export interface TimingMeasurement {
    error_bars?:                ErrorBars;
    personal_equation_applied?: boolean | null;
    /**
     * Visual only
     */
    personal_equation_s?: number | null;
    /**
     * RAW time in AUTO_CORRECTED mode; FINAL time in MANUALLY_CORRECTED mode
     */
    time_utc: Date;
}

export interface ErrorBars {
    /**
     * +/- s at 0.6827 CL
     */
    cl_68?: number | null;
    /**
     * +/- s at 0.9500 CL (primary accuracy)
     */
    cl_95?: number | null;
    /**
     * +/- s at 0.9973 CL
     */
    cl_9973?: number | null;
}

export enum TimingMode {
    AutoCorrected = "AUTO_CORRECTED",
    ManuallyCorrected = "MANUALLY_CORRECTED",
}
