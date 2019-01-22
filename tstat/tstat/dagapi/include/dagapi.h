/*
 * Copyright (c) 2004-2005 Endace Technology Ltd, Hamilton, New Zealand.
 * All rights reserved.
 *
 * This source code is proprietary to Endace Technology Limited and no part
 * of it may be redistributed, published or disclosed except as outlined in
 * the written contract supplied with this product.
 *
 * $Id: dagapi.h,v 1.63 2006-11-28 20:47:11 vladimir Exp $
 */

#ifndef DAGAPI_H
#define DAGAPI_H

/*****************************************************************************/
/* Includes                                                                  */
/*****************************************************************************/

/* DAG headers. */
#include "dagnew.h"
#include "dagreg.h"

#if (defined(__APPLE__) && defined(__ppc__))

#include <IOKit/IOKitLib.h>
#include <ppc_intrinsics.h>

#define dag_writel(val, reg)  __stwbrx((val), (reg), 0)
#define dag_readl(reg)        __lwbrx((reg), 0)

#elif defined(__FreeBSD__) || defined(__linux__) || (defined(__APPLE__) && defined(__i386__)) || (defined(__SVR4) && defined(__sun)) || defined(_WIN32)

/* Can't rely on autoconf's WORDS_BIGENDIAN here because we can't install config.h with the Endace headers.  
 * So we do our best to detect based on built-in compiler #defines.
 */
#if defined(__i386__) || defined(__x86_64__) || defined(_M_IX86) 

/* OK: known little-endian CPU. */
#define dag_writel(val, reg)  *(volatile uint32_t*)((reg)) = (val)
#define dag_readl(reg)        *(volatile uint32_t*)((reg))

#elif defined(__BIG_ENDIAN__) || defined(__ppc__) || defined(__POWERPC__)

/* Error: known big-endian CPU. */
#error Compiling for FreeBSD, Linux, Mac OS X, Solaris or Windows on a big-endian CPU is not supported.  Please contact <support@endace.com> for assistance.

#else

/* Error: unknown endianness CPU. */
#error Could not detect CPU endianness.  Please contact <support@endace.com> for assistance.

#endif /* big endian check */

#else
#error Compiling on an unsupported platform.  Please contact <support@endace.com> for assistance.
#endif /* Platform-specific code. */


/*****************************************************************************/
/* Macros and constants                                                      */
/*****************************************************************************/

/* GPP record type defines */
#define TYPE_LEGACY             0
#define TYPE_HDLC_POS           1
#define TYPE_ETH                2
#define TYPE_ATM                3
#define TYPE_AAL5               4
#define TYPE_MC_HDLC            5
#define TYPE_MC_RAW             6
#define TYPE_MC_ATM             7
#define TYPE_MC_RAW_CHANNEL     8
#define TYPE_MC_AAL5            9
#define TYPE_COLOR_HDLC_POS     10
#define TYPE_COLOR_ETH          11
#define TYPE_MC_AAL2            12
#define TYPE_IP_COUNTER         13
#define TYPE_TCP_FLOW_COUNTER   14
#define TYPE_DSM_COLOR_HDLC_POS 15
#define TYPE_DSM_COLOR_ETH      16
#define TYPE_COLOR_MC_HDLC_POS  17
#define TYPE_AAL2               18

#define TYPE_PAD                48

#define TYPE_MIN  1   /* sanity checking */
#define TYPE_MAX  48  /* sanity checking */

#define dag_record_size   16
#define DAGF_NONBLOCK     0x01  /* Deprecated, use dag_set_stream_poll(). */

#define MAX_INTERFACES 16

#define PBM_TX_DEFAULT_SIZE 16

/*****************************************************************************/
/* Platform-specific headers and macros                                      */
/*****************************************************************************/

#if defined(__FreeBSD__) || defined(__linux__) || (defined(__APPLE__) && defined(__ppc__))

#include <inttypes.h>
#include <sys/time.h>

#elif defined(__SVR4) && defined(__sun)

#define TIMEVAL_TO_TIMESPEC(tv, ts)							\
	do {													\
		(ts)->tv_sec = (tv)->tv_sec;						\
		(ts)->tv_nsec = (tv)->tv_usec * 1000;				\
	} while (0)
 
#define TIMESPEC_TO_TIMEVAL(tv, ts)							\
	do {													\
		(tv)->tv_sec = (ts)->tv_sec;						\
		(tv)->tv_usec = (ts)->tv_nsec / 1000;				\
	} while (0)

#define timeradd(tvp, uvp, vvp)								\
	do {													\
		(vvp)->tv_sec = (tvp)->tv_sec + (uvp)->tv_sec;		\
		(vvp)->tv_usec = (tvp)->tv_usec + (uvp)->tv_usec;	\
		if ((vvp)->tv_usec >= 1000000) {					\
			(vvp)->tv_sec++;								\
        	(vvp)->tv_usec -= 1000000;						\
        }													\
	} while (0)	
 
#elif defined(_WIN32)

/* Nothing here, but it allows the error below to catch unsupported platforms. */

#else
#error Compiling on an unsupported platform - please contact <support@endace.com> for assistance.
#endif /* Platform-specific code. */


/*****************************************************************************/
/* Data structures                                                           */
/*****************************************************************************/

/* GPP Type 1 */
typedef struct pos_rec {
	uint32_t          hdlc;
	uint8_t           pload[1];
} pos_rec_t;

/* GPP Type 2 */
typedef struct eth_rec {
	uint8_t           offset;
	uint8_t           pad;
	uint8_t           dst[6];
	uint8_t           src[6];
	uint16_t          etype;
	uint8_t           pload[1];
} eth_rec_t;

/* GPP Type 3 */
typedef struct atm_rec {
	uint32_t          header;
	uint8_t           pload[1];
} atm_rec_t;

/* GPP Type 4 */
typedef struct aal5_rec {
	uint32_t          header;
	uint8_t           pload[1];
} aal5_rec_t;

/* GPP Type 5  */
typedef struct mc_hdlc_rec {
	uint32_t          mc_header;
	uint8_t           pload[1];
} mc_hdlc_rec_t;

/* GPP Type 6  */
typedef struct mc_raw_rec {
	uint32_t          mc_header;
	uint8_t           pload[1];
} mc_raw_rec_t;

/* GPP Type 7  */
typedef struct mc_atm_rec {
	uint32_t          mc_header;
	uint8_t           pload[1];
} mc_atm_rec_t;

/* GPP Type 8  */
typedef struct mc_raw_channel_rec {
	uint32_t          mc_header;
	uint8_t           pload[1];
} mc_raw_channel_rec_t;

/* GPP Type 9  */
typedef struct mc_aal_rec {
	uint32_t          mc_header;
	uint8_t           pload[1];
} mc_aal_rec_t;

/* GPP Type 18 */
typedef struct aal2_rec {
	uint32_t          ext_header;
	uint32_t          header;
	uint8_t           pload[1];
} aal2_rec_t;

typedef struct flags {
	uint8_t           iface:2;
	uint8_t           vlen:1;
	uint8_t           trunc:1;
	uint8_t           rxerror:1;
	uint8_t           dserror:1;
	uint8_t           reserved:1;
	uint8_t           direction:1;
} flags_t;

/* GPP Global type */
typedef struct dag_record {
	uint64_t          ts;
	uint8_t           type;
	flags_t           flags;
	uint16_t          rlen;
	uint16_t          lctr;
	uint16_t          wlen;
	union {
		pos_rec_t       pos;
		eth_rec_t       eth;
		atm_rec_t       atm;
		aal5_rec_t      aal5;
		aal2_rec_t      aal2;
		mc_hdlc_rec_t   mc_hdlc;
		mc_raw_rec_t    mc_raw;
		mc_atm_rec_t    mc_atm;
		mc_aal_rec_t    mc_aal5;
		mc_aal_rec_t    mc_aal2;
		mc_raw_channel_rec_t mc_raw_channel;
	} rec;
} dag_record_t;

/*****************************************************************************/
/* Parameters set by user                                                    */
/*****************************************************************************/

#define DAG_FLUSH_RECORDS         0



/*****************************************************************************/
/* Function declarations                                                     */
/*****************************************************************************/

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/**
Obtain a file descriptor for a DAG card.
@param dagname The name of the device to open, e.g. "/dev/dag0", "dag0".
@return A UNIX-style file descriptor for the DAG device on success, otherwise -1 with errno set appropriately.
*/
int dag_open(char * dagname);

/**
Close a DAG card.
@param dagfd A file descriptor for a DAG device.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_close(int dagfd);

/**
Configure a DAG card.
@param dagfd A file descriptor for a DAG device.
@param params A whitespace-delimited configuration string.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_configure(int dagfd, char * params);

/**
Reserve a stream on a DAG card and map its memory buffer into the process' address space.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param flags A bitfield that modifies the behaviour of the routine.
@param extra_window_size How much extra address space to allocate.  0 means to allocate twice the stream size and is recommended for most users.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_attach_stream(int dagfd, int stream_num, uint32_t flags, uint32_t extra_window_size);

/**
Release a stream on a DAG card.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_detach_stream(int dagfd, int stream_num);

/**
Start transmitting/receiving on a stream.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_start_stream(int dagfd, int stream_num);

/**
Stop transmitting/receiving on a stream.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_stop_stream(int dagfd, int stream_num);

/**
Read the current polling parameters for a stream.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param[out] mindata The minimum amount of data to retrieve in bytes.  The default is 16 (the size of an ERF record header) and 0 puts the stream into non-blocking mode.
@param[out] maxwait The maximum amount of time the receive routines should wait before returning.  This overrides the mindata parameter.
@param[out] poll In case sufficient data has not arrived and the maximum time to wait has not expired, this parameter sets the interval at which the library will check to see if new data has arrived.  The default is 10 milliseconds.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_get_stream_poll(int dagfd, int stream_num, uint32_t * mindata, struct timeval * maxwait, struct timeval * poll);

/**
Set the polling parameters for a stream.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param[out] mindata The minimum amount of data to retrieve in bytes.  The default is 16 (the size of an ERF record header) and 0 puts the stream into non-blocking mode.
@param[out] maxwait The maximum amount of time the receive routines should wait before returning.  This overrides the mindata parameter.
@param[out] poll In case sufficient data has not arrived and the maximum time to wait has not expired, this parameter sets the interval at which the library will check to see if new data has arrived.  The default is 10 milliseconds.
@return 0 on success, otherwise -1 with errno set appropriately.
*/
int dag_set_stream_poll(int dagfd, int stream_num, uint32_t mindata, struct timeval * maxwait, struct timeval * poll);

/**
Read the size of the stream buffer in bytes.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return The size of the stream buffer on success, otherwise -1 with errno set appropriately.
*/
int dag_get_stream_buffer_size(int dagfd, int stream_num);

/**
Read the number of bytes currently outstanding in the stream buffer.  For transmit streams this is the number of bytes committed by the user but not yet transmitted by the card.  For receive streams this is the number of bytes available to the user for reading.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return The number of bytes outstanding in the stream buffer on success, otherwise -1 with errno set appropriately.
*/
int dag_get_stream_buffer_level(int dagfd, int stream_num);

/**
Read the last buffer level.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return
*/
int dag_get_stream_last_buffer_level (int dagfd, int stream_num);

/**
Read the number of receive streams supported by the DAG card with the currently loaded firmware.
@param dagfd A file descriptor for a DAG device.
@return The number of receive streams on success, otherwise -1 with errno set appropriately.
*/
int dag_rx_get_stream_count(int dagfd);

/**
Read the number of transmit streams supported by the DAG card with the currently loaded firmware.
@param dagfd A file descriptor for a DAG device.
@return The number of transmit streams on success, otherwise -1 with errno set appropriately.
*/
int dag_tx_get_stream_count(int dagfd);

/**
Block/Record transmit allocator - zero copy.  Provides a pointer to the requested number of bytes of available space for the specified stream.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param size The number of bytes requested.
@return A pointer to a block of at least the requested size on success, otherwise NULL with errno set appropriately.
*/
uint8_t * dag_tx_get_stream_space(int dagfd, int stream_num, uint32_t size);

/**
Block oriented transmit interface - zero copy.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param size The number of bytes to commit (transmit).
@return A pointer to a block of at least the requested size on success, otherwise NULL with errno set appropriately.
*/
uint8_t * dag_tx_stream_commit_bytes(int dagfd, int stream_num, uint32_t size);

/**
Block oriented transmit interface - COPIES DATA.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param orig A pointer to the beginning of the first ERF record to be copied.
@param size The number of bytes to copy.
@return The number of bytes written on success, otherwise -1 with errno set appropriately.
*/
int dag_tx_stream_copy_bytes(int dagfd, int stream_num, uint8_t * orig, uint32_t size);

/**
Record oriented receive interface - zero copy.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@return A pointer to a single ERF record on success, otherwise NULL with errno set appropriately.
*/
uint8_t * dag_rx_stream_next_record(int dagfd, int stream_num);

/**
Record oriented receive and transmit for inline forwarding.
@param dagfd A file descriptor for a DAG device.
@param rx_stream_num Which receive stream to use.
@param tx_stream_num Which receive stream to use.
@return A pointer to a single ERF record on success, otherwise NULL with errno set appropriately.
*/
uint8_t * dag_rx_stream_next_inline (int dagfd, int rx_stream_num, int tx_stream_num);

/**
Traditional ringbuffer interface - zero copy.  Replaces dag_offset().
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use.
@param bottom A pointer to the location in the buffer up to which the application has processed.  Should be NULL on the first call.
@return A pointer to the top of available buffer space on success, otherwise NULL with errno set appropriately.
*/
uint8_t * dag_advance_stream(int dagfd, int stream_num, uint8_t ** bottom);

/**
Receives errno from the DAG API.
@return An error code.
*/
int dag_get_last_error(void);


/**
Sets a general attribute in the DAG API.
@param dagfd A file descriptor for a DAG device.
@param stream_num Which stream to use if required otherwise -1.
@param param The parameter to be set.
@param value Pointer to the value the parameter should be given
@return 0 on success otherwise -1 with errno set appropriately.
*/
int dag_set_param(int dagfd, int stream_num, uint32_t param, void *value);



/*****************************************************************************/
/* Deprecated Function declarations - provided for code compatibility only   */
/*****************************************************************************/
int dag_start(int dagfd);
int dag_stop(int dagfd);
void * dag_mmap(int dagfd);
int dag_offset (int dagfd, int * oldoffset, int flags);
void dag_getpollparams(int * mindatap, struct timeval * maxwait, struct timeval * poll);
void dag_setpollparams(int mindata, struct timeval * maxwait, struct timeval * poll);
int dag_clone(int dagfd, int minor);



/* Subject to change */
daginf_t * dag_info(int dagfd);
uint8_t * dag_iom(int dagfd);

/* libpcap helper */
uint8_t dag_linktype(int dagfd);
int dag_get_erf_types(int dagfd, uint8_t * erfs, int size);


/* General helper function - here temporarily, will eventually be put in dagutil.c
 *
 * name is the user-supplied string specifying a DAG device and stream.
 *   e.g. "/dev/dag0:2", "dag0:2", "0:2", "/dev/dag0", "dag0", "0", ""
 *
 * The canonical version of the name ("/dev/dag0") and the stream number are 
 * returned in buffer (which has length buflen) and stream_number respectively.
 * Returns -1 and sets errno on failure (most likely because name couldn't be
 * matched against any of the above templates).
 */

int dag_parse_name(const char * name, char * buffer, int buflen, int * stream_number);

char* dag_getname(int dagfd);

/* Buffer size for use with dag_parse_name(). */
#define DAGNAME_BUFSIZE 128

void* GetMmapRegion(int iDagFd, int iStream);

#ifdef __cplusplus
}
#endif /* __cplusplus */


#endif /* DAGAPI_H */
