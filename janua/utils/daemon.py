# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
##
#
# Copyright 2007 Sander Marechal (http://www.jejik.com)
#
# http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#
##

import os
import stat
import sys
import signal
import time


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', logfile='/var/log/janua.log', uid=0, gid=0):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.logfile = logfile
        self.uid = uid
        self.gid = gid

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try: 
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0)

        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e: 
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1) 

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        if os.path.exists(self.logfile) == False:
            fd = file(self.logfile,'w+')
            fd.close()
        se = file(self.logfile,'a+')
        so = file(self.stdout, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        pid = str(os.getpid())
        pidfile = file(self.pidfile,'w+')
        pidfile.write('%s\n' % pid)
        pidfile.close()

        # drop privileges
        logdir = os.path.dirname(self.logfile)
        if not os.path.exists(logdir):
            os.mkdir(logdir)
            os.chown(logdir, self.uid, self.gid)
            os.chmod(logdir, stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP)

        os.chown(self.logfile, self.uid, self.gid)
        os.chmod(self.logfile, stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP)
        os.setresgid(self.gid, self.gid, self.gid)
        os.setresuid(self.uid, self.uid, self.uid)

    def start(self, *args, **kwargs):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            # check if it really run because when process crash or killed
            # it doesn't remove pid file
            try:
                proc_path = '/proc/%d/cmdline' % pid
                proc_file = file(proc_path, 'r')
                ps_cmdline = proc_file.read().strip()
                if 'janua' in ps_cmdline:
                    message = 'Janua already running\n'
                    sys.stderr.write(message)
                    sys.exit(1)
                else:
                    os.remove(self.pidfile)
                proc_file.close()
            except IOError:
                # there is no process running, remove pidfile
                os.remove(self.pidfile)

        # Start the daemon
        self.daemonize()
        self.run(*args, **kwargs)

    def stop(self):
        """
        Stop the daemon
        """      
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = 'pidfile %s does not exist. Daemon not running ?\n'
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process	
        try:
            os.kill(pid, signal.SIGTERM)
            
            # it's not possible to wait a non child process
            # so the idea is to check if pid is running
            # ugly but heh its better than a simple blind sleep
            timeout = 0.0
            while timeout < 10.0:
                try:
                    os.kill(pid, 0)
                except OSError:
                    time.sleep(0.2)
                    timeout += 0.2
                    continue
                else:
                    os.remove(self.pidfile)
                    break

        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def status(self):
        """
        Daemon status
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = 'Running'
        else:
            message = 'Stopped'

        sys.stdout.write('%s\n' % message)
        sys.exit(0)

    def run(self, *args, **kwargs):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
