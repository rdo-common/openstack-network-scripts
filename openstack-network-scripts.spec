%global _hardened_build 1

# =============================================================================

Name:             openstack-network-scripts
Summary:          Legacy scripts for manipulating of network devices
Version:          10.09
Release:          1%{?dist}

License:          GPLv2

URL:              https://github.com/fedora-sysv/initscripts
Source:           https://github.com/fedora-sysv/initscripts/archive/%{version}.tar.gz#/initscripts-%{version}.tar.gz

Requires:         initscripts >= %{version}-%{release}

Requires:         bash
Requires:         bc
Requires:         coreutils
Requires:         dbus
Requires:         filesystem          >= 3
Requires:         gawk
Requires:         grep
Requires:         hostname
Requires:         ipcalc
Requires:         iproute
Requires:         kmod
Requires:         procps-ng
Requires:         sed
Requires:         systemd

Requires(post):   chkconfig
Requires(preun):  chkconfig

Requires(post):   %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

BuildRequires:    filesystem          >= 3
BuildRequires:    gcc
BuildRequires:    gettext
BuildRequires:    git
BuildRequires:    glib2-devel
BuildRequires:    make
BuildRequires:    pkgconfig
BuildRequires:    popt-devel
BuildRequires:    setup

%{?systemd_requires}
BuildRequires:    systemd

Obsoletes:        network-scripts            < 9.82-2
Provides:         network-scripts = %{version}-%{release}

%description
This package contains the legacy scripts for activating & deactivating of most
network interfaces. It also provides a legacy version of 'network' service.

The 'network' service is enabled by default after installation of this package,
and if the network-scripts are installed alongside NetworkManager, then the
ifup/ifdown commands from network-scripts take precedence over the ones provided
by NetworkManager.


# === BUILD INSTRUCTIONS ======================================================

%prep
%setup -q -n initscripts-%{version}

# ---------------

%build
%{__make} \
    %{_make_output_sync} \
    %{?_smp_mflags} \
    %{_make_verbose} \
  make-binaries

# ---------------

%install

rm -rf %{buildroot}%{_sysconfdir}/network-scripts
install -m 0755 -d %{buildroot}%{_sysconfdir}/rc.d/init.d/
install -m 0755 -d %{buildroot}%{_prefix}
install -m 0755 -d %{buildroot}%{_sysconfdir}/sysconfig/network-scripts
install -m 0755 -d %{buildroot}%{_mandir}/man8
# Additional ways to access documentation:
install -m 0755 -d %{buildroot}%{_docdir}/network-scripts
install -m 0755 -d %{buildroot}%{_sbindir}

install -m 0755 %{_builddir}/initscripts-%{version}/etc/rc.d/init.d/network %{buildroot}%{_sysconfdir}/rc.d/init.d/
cp -a network-scripts/* %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/
install -m 0644 man/{ifup,usernetctl}.8 %{buildroot}%{_mandir}/man8

# Not supported interfaces
# s390
rm -f %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/ifup-ctc
# serial
rm -f %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/if{down,up}-sit
# wireless
rm -f %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/ifup-wireless
# plip
rm -f %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/ifup-pl{ip,usb}
# bluetooth
rm -f %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/if{down,up}-bnep
# ippp
rm -f %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/if{down,up}-ippp


ln -s  %{_docdir}/initscripts/sysconfig.txt %{buildroot}%{_docdir}/network-scripts/
ln -sr %{_mandir}/man8/ifup.8           %{buildroot}%{_mandir}/man8/ifdown.8

install -m 0755 %{_builddir}/initscripts-%{version}/src/build/usernetctl %{buildroot}%{_sbindir}/

# We are now using alternatives approach to better co-exist with NetworkManager:
touch %{buildroot}%{_sbindir}/ifup
touch %{buildroot}%{_sbindir}/ifdown

# =============================================================================

%post
chkconfig --add network > /dev/null 2>&1 || :

[ -L %{_sbindir}/ifup ]   || rm -f %{_sbindir}/ifup
[ -L %{_sbindir}/ifdown ] || rm -f %{_sbindir}/ifdown

%{_sbindir}/update-alternatives --install %{_sbindir}/ifup   ifup   %{_sysconfdir}/sysconfig/network-scripts/ifup 90 \
                                --slave   %{_sbindir}/ifdown ifdown %{_sysconfdir}/sysconfig/network-scripts/ifdown \
                                --initscript network

%preun
if [ $1 -eq 0 ]; then
  chkconfig --del network > /dev/null 2>&1 || :
  %{_sbindir}/update-alternatives --remove ifup %{_sysconfdir}/sysconfig/network-scripts/ifup
fi

# === PACKAGING INSTRUCTIONS ==================================================

%files
%license COPYING

%doc doc/examples/
%dir %{_sysconfdir}/sysconfig/network-scripts

%{_sysconfdir}/rc.d/init.d/network
%{_sysconfdir}/sysconfig/network-scripts/*

%config(noreplace)    %{_sysconfdir}/sysconfig/network-scripts/ifcfg-lo

%ghost                %{_sbindir}/ifup
%ghost                %{_sbindir}/ifdown
%attr(4755,root,root) %{_sbindir}/usernetctl

%{_mandir}/man8/ifup.*
%{_mandir}/man8/ifdown.*
%{_mandir}/man8/usernetctl.*
%{_docdir}/network-scripts/*

# =============================================================================

%changelog
* Mon Jul 19 2021 Alex Schultz <aschultz@redhat.com> - 10.09-1
- OpenStack specific network scripts package from initscripts
