/*
 * Copyright (c) 2002-2005 Endace Technology Ltd, Hamilton, New Zealand.
 * All rights reserved.
 *
 * This source code is proprietary to Endace Technology Limited and no part
 * of it may be redistributed, published or disclosed except as outlined in
 * the written contract supplied with this product.
 *
 * $Id: dagutil.h,v 1.34 2006-11-29 01:56:37 ben Exp $
 */

#ifndef DAGUTIL_H
#define DAGUTIL_H

/* DAG headers. */
#include "dag_platform.h"
#include "dagnew.h"
#include "dagreg.h"
#include "dagpci.h"


/* Macros defined on some platforms but not others. */
#ifndef LINE_MAX
#define LINE_MAX 1024
#endif /* LINE_MAX */

#ifndef PATH_MAX
#define PATH_MAX 1024
#endif /* PATH_MAX */

#ifndef O_LARGEFILE
#define O_LARGEFILE 0
#endif /* O_LARGEFILE */

#ifndef O_DIRECT
#define O_DIRECT 0
#endif /* O_DIRECT */

#ifndef UINT8_MAX
#define UINT8_MAX 255
#endif /* UINT8_MAX */

#ifndef UINT16_MAX
#define UINT16_MAX 65535
#endif /* UINT16_MAX */


/* SI units. */
#ifndef ONE_KIBI
#define ONE_KIBI (1024)
#endif /* ONE_KIBI */

#ifndef ONE_MEBI
#define ONE_MEBI (1048576)
#endif /* ONE_MEBI */

#ifndef ONE_GIBI
#define ONE_GIBI (1073741824)
#endif /* ONE_GIBI */

#ifndef ONE_TEBI
#define ONE_TEBI (1099511627776ULL)
#endif /* ONE_TEBI */


/* Useful cross-platform macros. 
 * Prefixed with "dagutil_" to avoid conflicts with client code.
 */
#ifndef dagutil_min
#define dagutil_min(X,Y) ((X)>(Y))?(Y):(X)
#endif /* dagutil_min */

#ifndef dagutil_max
#define dagutil_max(X,Y) ((X)>(Y))?(X):(Y)
#endif /* dagutil_max */



/**
 * Macro to calculate the number of items in an array
 */
#ifndef dagutil_arraysize
#define dagutil_arraysize(X) ((sizeof(X))/(sizeof(*X)))
#endif /* dagutil_arraysize */



/**
 * Sempahore type returned when the semaphore is created and should be used in
 * all subsequent semaphore accesses.
 *
 */
#if defined(__FreeBSD__) || defined(__linux__) || (defined(__SVR4) && defined(__sun)) || (defined(__APPLE__) && defined(__ppc__))

struct dagutil_sem_s {
	sem_t *sem_p;
	int    named;
	char  *name_p;
};
typedef struct dagutil_sem_s*  dagutil_sem_t;
#define DAGUTIL_INVALID_SEM_TYPE     NULL

#elif defined(_WIN32)

typedef HANDLE  dagutil_sem_t;
#define DAGUTIL_INVALID_SEM_TYPE     NULL

#endif


/**
 * Constant used for the dagutil set of synchronisation functions, as a timeout
 * value that indicates that the function should block until the condition is
 * signaled or there is an error.
 */
#define DAGUTIL_WAIT_FOREVER     (uint32_t)-1




/**
 * Mutex type returned when the mutex object is created and should
 * be used when locking and unlocking a mutex.
 *
 */
#if defined(__FreeBSD__) || defined(__linux__) || (defined(__SVR4) && defined(__sun)) || (defined(__APPLE__) && defined(__ppc__))

typedef pthread_mutex_t* dagutil_mutex_t;
#define DAGUTIL_INVALID_MUTEX_TYPE     NULL

#elif defined(_WIN32)

typedef HANDLE           dagutil_mutex_t;
#define DAGUTIL_INVALID_MUTEX_TYPE     NULL

#endif



/**
 * The function pointer type past to the dagutil_create_thread function as
 * an entry point for the thread.
 */
#if defined(__FreeBSD__) || defined(__linux__) || (defined(__SVR4) && defined(__sun)) || (defined(__APPLE__) && defined(__ppc__))

typedef int              dagutil_thread_return_t;
typedef pthread_t        dagutil_thread_id_t;

#elif defined(_WIN32)

typedef DWORD            dagutil_thread_return_t;
typedef DWORD            dagutil_thread_id_t;

#endif

typedef dagutil_thread_return_t (*dagutil_thread_proc_t)(void*);





/**
 * This type defines dagutil time. It is structure almost identical to the
 * timeval defined by IEEE, except the field names are different and rather
 * than a micosecond field there is a nanosecond field. It has two fields
 * sec and nsec. The actual time value is computed by: sec + (nsec * 10^9)
 *
 */
typedef struct dagutil_time_s
{
	uint32_t  sec;          /**< seconds */
	int32_t   nsec;         /**< nanoseconds */
} dagutil_time_t;


/**
 * Compares two dagutil_time_t values and returns true if they are equal
 * otherwise false is returned.
 *
 * @param[in] x    First dagutil_time_t type to compare.
 * @param[in] y    Second dagutil_time_t type to compare.
 */
#define DAGUTIL_TIME_EQUAL(x, y)     \
	( ((x).sec == (y).sec) && ((x).nsec == (y).nsec) )

/**
 * Compares two dagutil_time_t values and returns true if x is greater than y
 * otherwise false is returned.
 *
 * @param[in] x    First dagutil_time_t type to compare.
 * @param[in] y    Second dagutil_time_t type to compare.
 */
#define DAGUTIL_TIME_GT(x, y)        \
	( ((x).sec > (y).sec) || (((x).sec == (y).sec) && ((x).nsec > (y).nsec)) )

/**
 * Compares two dagutil_time_t values and returns true if x is less than y
 * otherwise false is returned.
 *
 * @param[in] x    First dagutil_time_t type to compare.
 * @param[in] y    Second dagutil_time_t type to compare.
 */
#define DAGUTIL_TIME_LT(x, y)        \
	( ((x).sec < (y).sec) || (((x).sec == (y).sec) && ((x).nsec < (y).nsec)) )

/**
 * Performs a x += y operation.
 *
 * @param[in] x    dagutil_time_t type.
 * @param[in] y    dagutil_time_t type.
 */
#define DAGUTIL_TIME_ADD(x, y)                   \
	do {                                     \
		(x).sec  += (y).sec;             \
		(x).nsec += (y).nsec;            \
		DAGUTIL_TIME_NORMALIZE(x);       \
	} while (0)

/**
 * Performs a x -= y operation.
 *
 * @param[in] x    dagutil_time_t type.
 * @param[in] y    dagutil_time_t type.
 */
#define DAGUTIL_TIME_SUB(x, y)                   \
	do {                                     \
		(x).sec  -= (y).sec;             \
		(x).nsec -= (y).nsec;            \
		DAGUTIL_TIME_NORMALIZE(x);       \
	} while (0)

/**
 * Performs a z = x - y operation, that is it returns the difference between
 * time values.
 *
 * @param[in]  x   dagutil_time_t type.
 * @param[in]  y   dagutil_time_t type.
 * @param[out] z   dagutil_time_t type.
 */
#define DAGUTIL_TIME_DIFF(x, y, z)               \
	do {                                     \
		(z).sec  = (x).sec  - (y).sec;   \
		(z).nsec = (x).nsec - (y).nsec;  \
		DAGUTIL_TIME_NORMALIZE(z);       \
	} while (0)

/**
 * Performs a x = y operation, that is it equates the value of y to x.
 *
 * @param[in] x    dagutil_time_t type.
 * @param[in] y    dagutil_time_t type.
 */
#define DAGUTIL_TIME_SET(x, y)                   \
	do {                                     \
		(x).sec  = (y).sec;              \
		(x).nsec = (y).nsec;             \
	} while (0)

/**
 * Checks if the nsec value exceeds 1 billion (1 second) or is a negative value
 * and if so adds or subtracts 1 from the seconds value and adjusts the nanosecond
 * value accordingly.
 *
 * @param[in] x    dagutil_time_t type.
 */
#define DAGUTIL_TIME_NORMALIZE(x)                                     \
	while ( ((x).nsec >= 1000000000L) || ((x).nsec < 0) ) {       \
		if ((x).nsec >= 1000000000L)                          \
		{ (x).sec++; (x).nsec -= 1000000000L; }               \
		else if ((x).nsec < 0)                                \
		{ (x).sec--; (x).nsec += 1000000000L; }               \
	}




/* Useful bit constant macros. */
enum
{
	BIT0  = (1<<0),
	BIT1  = (1<<1),
	BIT2  = (1<<2),
	BIT3  = (1<<3),
	BIT4  = (1<<4),
	BIT5  = (1<<5),
	BIT6  = (1<<6),
	BIT7  = (1<<7),
	BIT8  = (1<<8),
	BIT9  = (1<<9),
	BIT10 = (1<<10),
	BIT11 = (1<<11),
	BIT12 = (1<<12),
	BIT13 = (1<<13),
	BIT14 = (1<<14),
	BIT15 = (1<<15),
	BIT16 = (1<<16),
	BIT17 = (1<<17),
	BIT18 = (1<<18),
	BIT19 = (1<<19),
	BIT20 = (1<<20),
	BIT21 = (1<<21),
	BIT22 = (1<<22),
	BIT23 = (1<<23),
	BIT24 = (1<<24),
	BIT25 = (1<<25),
	BIT26 = (1<<26),
	BIT27 = (1<<27),
	BIT28 = (1<<28),
	BIT29 = (1<<29),
	BIT30 = (1<<30),
	BIT31 = (1<<31)
};


typedef struct pbm_offsets
{
	uint32_t globalstatus;  /*  Global status. */
	uint32_t streambase;    /*  Offset of first stream. */
	uint32_t streamsize;    /*  Size of each stream. */
	uint32_t streamstatus;  /*  Control / Status. */
	uint32_t mem_addr;      /*  Mem hole base address. */
	uint32_t mem_size;      /*  Mem hole size. */
	uint32_t record_ptr;    /*  Record pointer. */
	uint32_t limit_ptr;     /*  Limit pointer. */
	uint32_t safetynet_cnt; /*  At limit event pointer. */
	uint32_t drop_cnt;      /*  Drop counter. */
	
} pbm_offsets_t;


/* 
 * This part controls fan and thermal information
 */
enum
{
	LM63_TEMP_LOC   = 0x00,
	LM63_TEMP_REM_H = 0x01,
	LM63_CONF       = 0x03,
	LM63_LOC_HIGH   = 0x05,
	LM63_REM_HIGH   = 0x07,
	
	LM63_ALERT_MASK = 0x16,
	
	LM63_PWM_RPM    = 0x4a,
	LM63_SPINUP     = 0x4b,
	LM63_PWM_VALUE  = 0x4c,

	LM63_LOOKUP_T1  = 0x50,
	LM63_LOOKUP_P1  = 0x51,
	LM63_LOOKUP_T2  = 0x52,
	LM63_LOOKUP_P2  = 0x53,
	LM63_LOOKUP_T3  = 0x54,
	LM63_LOOKUP_P3  = 0x55,
	LM63_LOOKUP_T4  = 0x56,
	LM63_LOOKUP_P4  = 0x57,
	LM63_LOOKUP_T5  = 0x58,
	LM63_LOOKUP_P5  = 0x59,
	LM63_LOOKUP_T6  = 0x5a,
	LM63_LOOKUP_P6  = 0x5b,
	LM63_LOOKUP_T7  = 0x5c,
	LM63_LOOKUP_P7  = 0x5d,
	LM63_LOOKUP_T8  = 0x5e,
	LM63_LOOKUP_P8  = 0x5f,
	
	LM63_REM_TEMP_FILTER = 0xbf,
	
	LM63 = 0x98
};


/* Consistent release version string. */
extern const char* const kDagReleaseVersion;

/* Consistent release version string "debug", "production". */
extern const char* const kDagBuildType;

/* Compiler flags string. */
extern const char* const kDagCompilerFlags;


#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/*
 * WARNING: routines in the dagutil module are provided for convenience
 *          and to promote code reuse among the dag* tools.
 *          They are subject to change without notice.
 */


/* Miscellaneous routines. */
void dagutil_set_progname(const char* program_name);
const char* dagutil_get_progname(void);
void dagutil_set_signal_handler(void (*handler)(int));
void dagutil_set_timer_handler(void (*handler)(int), uint32_t seconds);

/* Output routines. */
void dagutil_set_verbosity(int v);
int dagutil_get_verbosity(void);
void dagutil_inc_verbosity(void);
void dagutil_dec_verbosity(void);
void dagutil_panic(const char* fmt, ...) __attribute__((noreturn, format (printf, 1, 2)));
void dagutil_error(const char* fmt, ...) __attribute__((format (printf, 1, 2)));
void dagutil_warning(const char* fmt, ...) __attribute__((format (printf, 1, 2)));
void dagutil_verbose(const char* fmt, ...) __attribute__((format (printf, 1, 2)));
void dagutil_verbose_level(uint32_t level, const char* fmt, ...) __attribute__((format (printf, 2, 3)));

/* Sleeping routines. */
void dagutil_microsleep(uint32_t usecs);
void dagutil_nanosleep(uint32_t nanoseconds);
void dagutil_tsc64_read(uint64_t* tsc);
void dagutil_tsc32_read(uint32_t* tsc);

/* Timming routines. */
int dagutil_get_time(dagutil_time_t *time_p);

/* Synchronisation routines */
int dagutil_semaphore_init (dagutil_sem_t *sem_p, int initial, const char *name);
int dagutil_semaphore_take (dagutil_sem_t sem, uint32_t timeout);
int dagutil_semaphore_give (dagutil_sem_t sem);
int dagutil_semaphore_delete (dagutil_sem_t sem);
int dagutil_mutex_init (dagutil_mutex_t *mutex_p, int initial);
int dagutil_mutex_lock (dagutil_mutex_t mutex, uint32_t timeout);
int dagutil_mutex_unlock (dagutil_mutex_t mutex);
int dagutil_mutex_delete (dagutil_mutex_t mutex);

/* Threading routines */
int dagutil_thread_create (dagutil_thread_proc_t proc, void *arg, dagutil_thread_id_t *id_p);
void dagutil_thread_exit () __attribute__((noreturn));
int dagutil_thread_kill (dagutil_thread_id_t id);
int dagutil_thread_get_id (dagutil_thread_id_t *id_p);



/* I/O routines. */
void* dagutil_readfile(char *filename, char *flags, unsigned int* out_length);

/* Hooks for memory allocation/free. */
void* dagutil_malloc(size_t size);
void dagutil_free(void* ptr);
const char* dagutil_strdup(const char* source);

/* Coprocessor detect. */
coprocessor_t dagutil_detect_coprocessor(volatile uint8_t* dagiom);
bool dagutil_coprocessor_programmed(volatile uint8_t* iom);

/* Routines that were duplicated in dagthree, dagfour, dagsix, dagseven. */
pbm_offsets_t* dagutil_get_pbm_offsets(void);
int dagutil_lockstream(int dagfd, int stream);
int dagutil_unlockstream(int dagfd, int stream);
int dagutil_lockallstreams(int dagfd);
void dagutil_unlockallstreams(int dagfd);
uint32_t dagutil_iomread(volatile uint8_t* iom, uint32_t addr);
void dagutil_iomwrite(volatile uint8_t* iom, uint32_t addr, uint32_t value);
void dagutil_steerstatus(int dagfd, volatile uint8_t* dagiom, uint32_t base, int ver);
void dagutil_pbmstatus(int dagfd, volatile uint8_t* dagiom, uint32_t pbm_base, daginf_t* daginf, int pbm_ver);
int dagutil_pbmdefault(int dagfd, volatile uint8_t* dagiom, uint32_t pbm_base, daginf_t* daginf, int pbm_ver);
int dagutil_pbmconfigmem(int dagfd, volatile uint8_t* dagiom, uint32_t pbm_base, daginf_t* daginf, int pbm_ver, const char* cstr);
int dagutil_pbmconfigmemoverlap(int dagfd, volatile uint8_t* dagiom, uint32_t pbm_base, daginf_t* daginf, int pbm_ver);
void dagutil_reset_datapath(volatile uint8_t* iom);
#if defined(__FreeBSD__) || defined(__linux__) || (defined(__SVR4) && defined(__sun)) || (defined(__APPLE__) && defined(__ppc__))
int dag82x_open_2nd_core(const char* dagname_1st_core);
#elif defined(_WIN32)
HANDLE dag82x_open_2nd_core(const char* dagname_1st_core);
#endif

/* Translate a physical line to a logical line number.  This was duplicated in several places too: dagbits, dagpartum (twice).
 * It's still in the dag37t_api library.
 */
uint32_t dagutil_37t_line_get_logical(uint32_t uline);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* DAGUTIL_H */ 
