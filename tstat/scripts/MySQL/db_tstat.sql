--
-- Table structure for table tcp
--

-- DROP TABLE IF EXISTS tcp;
CREATE TABLE tcp (
  id int(11) NOT NULL auto_increment,
  src_ip int(10) unsigned NOT NULL default "0",
  src_port smallint(5) unsigned NOT NULL default "0",
  src_data int(10) unsigned default NULL,
  src_packet int(10) unsigned default NULL,
  dst_ip int(10) unsigned NOT NULL default "0",
  dst_port smallint(5) unsigned NOT NULL default "0",
  dst_data int(10) unsigned default NULL,
  dst_packet int(10) unsigned default NULL,
  starttime double NOT NULL default "0",
  duration double NOT NULL default "0",
  src_internal tinyint(1) default NULL,
  dst_internal tinyint(1) default NULL,
  conn_type set("HTTP","RSTP","RTP","ICY","RTCP","MSN","YMSG","XMPP","P2P","SKYPE","SMTP","POP3","IMAP","SSL","OBF","SSH","RTMP","MSE_PE") NOT NULL default "",
  p2p_type set("","ED2K","DATA_KAZAA","DATA_ED2K","DATA_DC","DC","DATA_GNU","GNU","KAZAA","BIT","APPLE","SOUL","WINMX","ARES","MUTE","WASTE","XDCC","KAD","KADU") NOT NULL default "",
  ed2k_data smallint(5) unsigned default NULL,
  ed2k_sig smallint(5) unsigned default NULL,
  ed2k_c2s smallint(5) unsigned default NULL,
  ed2k_c2c smallint(5) unsigned default NULL,
  ed2k_msg smallint(5) unsigned default NULL,
  src_max_seg_size smallint(5) unsigned default NULL,
  dst_max_seg_size smallint(5) unsigned default NULL,
  html enum ("NONE","GET","POST","MSN","RTMPT","YOUTUBE","VIDEOCONTENT","VIMEO","WIKI","RAPIDSHARE","MEGAUPLOAD","FACEBOOK","ADV","FLICKR","GMAPS","VOD","YOUTUBESITE","SOCIAL","FLASHVIDEO","MEDIAFIRE","HOTFILE","STORAGE","YOUTUBE204","YOUTUBE204VIDEO","YOUTUBESITEDIRECT","YOUTUBESITEEMBED") NOT NULL  default "GET",
  PRIMARY KEY  (id),
  KEY idx_src_ip (src_ip),
  KEY idx_src_port (src_port),
  KEY idx_dst_ip (dst_ip),
  KEY idx_dest_ip (dst_port),
  KEY idx_src_sock (src_ip,src_port),
  KEY idx_dst_sock (dst_ip,dst_port),
  KEY idx_src_dst (src_ip,dst_ip)
);

--
-- Table structure for table tcp_no
--

-- DROP TABLE IF EXISTS tcp_no;
CREATE TABLE tcp_no (
  id int(11) NOT NULL auto_increment,
  src_ip int(10) unsigned NOT NULL default "0",
  src_port smallint(5) unsigned NOT NULL default "0",
  src_packet smallint(5) unsigned default NULL,
  src_syn smallint(5) unsigned default NULL,
  src_rst smallint(5) unsigned default NULL,
  src_ack smallint(5) unsigned default NULL,
  src_fin smallint(5) unsigned default NULL,
  dst_ip int(10) unsigned NOT NULL default "0",
  dst_port smallint(5) unsigned NOT NULL default "0",
  dst_packet smallint(5) unsigned default NULL,
  dst_syn smallint(5) unsigned default NULL,
  dst_rst smallint(5) unsigned default NULL,
  dst_ack smallint(5) unsigned default NULL,
  dst_fin smallint(5) unsigned default NULL,
  starttime double NOT NULL default "0",
  duration double NOT NULL default "0",
  src_internal tinyint(1) default NULL,
  dst_internal tinyint(1) default NULL,
  PRIMARY KEY  (id),
  KEY idx_src_ip (src_ip),
  KEY idx_src_port (src_port),
  KEY idx_dst_ip (dst_ip),
  KEY idx_dest_ip (dst_port),
  KEY idx_src_sock (src_ip,src_port),
  KEY idx_dst_sock (dst_ip,dst_port),
  KEY idx_src_dst (src_ip,dst_ip)
);

--
-- Table structure for table udp
--

-- DROP TABLE IF EXISTS udp;
CREATE TABLE udp (
  id int(11) NOT NULL auto_increment,
  src_ip int(10) unsigned NOT NULL default "0",
  src_port smallint(5) unsigned NOT NULL default "0",
  src_starttime double NOT NULL default "0",
  src_duration double NOT NULL default "0",
  src_data int(10) unsigned default NULL,
  src_packet int(10) unsigned default NULL,
  src_internal tinyint(1) default NULL,
  src_type enum("unknown","ed2k","kad","kadu","okad","gnu","bt","dc","kazaa","rtp","rtcp","skype_e2e","skype_out","skype_sig","pplive","sopcast","tvants","dns","utp","utpbt","vod","ppstream","teredo") NOT NULL default "unknown",
  dst_ip int(10) unsigned NOT NULL default "0",
  dst_port smallint(5) unsigned NOT NULL default "0",
  dst_starttime double NOT NULL default "0",
  dst_duration double NOT NULL default "0",
  dst_data int(10) unsigned default NULL,
  dst_packet int(10) unsigned default NULL,
  dst_internal tinyint(1) default NULL,
  dst_type enum("unknown","ed2k","kad","kadu","okad","gnu","bt","dc","kazaa","rtp","rtcp","skype_e2e","skype_out","skype_sig","pplive","sopcast","tvants","dns","utp","utpbt","vod","ppstream","teredo") NOT NULL default "unknown",
  PRIMARY KEY  (id),
  KEY idx_src_ip (src_ip),
  KEY idx_src_port (src_port),
  KEY idx_dst_ip (dst_ip),
  KEY idx_dest_ip (dst_port),
  KEY idx_src_sock (src_ip,src_port),
  KEY idx_dst_sock (dst_ip,dst_port),
  KEY idx_src_dst (src_ip,dst_ip)
);

