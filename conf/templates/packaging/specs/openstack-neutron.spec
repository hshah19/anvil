#encoding UTF-8
# Based on spec by:
# * Terry Wilson <twilson@redhat.com>
# * Alan Pevec <apevec@redhat.com>
# * Martin Magr <mmagr@redhat.com>
# * Gary Kotton <gkotton@redhat.com>
# * Robert Kukura <rkukura@redhat.com>
# * Pádraig Brady <P@draigBrady.com>


%global python_name neutron
%global daemon_prefix openstack-neutron
%global os_version $version
%global no_tests $no_tests
%global tests_data_dir %{_datarootdir}/%{python_name}-tests

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 6)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:		openstack-neutron
Version:        %{os_version}$version_suffix
Release:        $release%{?dist}
Epoch:          $epoch
Summary:	Virtual network service for OpenStack (neutron)

Group:		Applications/System
License:	ASL 2.0
URL:		http://launchpad.net/neutron/

Source0:        %{python_name}-%{os_version}.tar.gz
Source1:	neutron.logrotate
Source2:	neutron-sudoers

Source10:	neutron-server.init
Source11:	neutron-linuxbridge-agent.init
Source12:	neutron-openvswitch-agent.init
Source13:	neutron-ryu-agent.init
Source14:	neutron-nec-agent.init
Source15:	neutron-dhcp-agent.init
Source16:	neutron-l3-agent.init
Source17:	neutron-ovs-cleanup.init
Source18:	neutron-hyperv-agent.init
Source19:	neutron-rpc-zmq-receiver.init
Source20:	neutron-metadata-agent.init

#for $idx, $fn in enumerate($patches)
Patch$idx: $fn
#end for

BuildArch:	noarch

BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildRequires:	python-pbr
# Build require these parallel versions
# as setup.py build imports neutron.openstack.common.setup
# which will then check for these
# BuildRequires:	python-sqlalchemy
# BuildRequires:	python-webob
# BuildRequires:	python-paste-deploy
# BuildRequires:	python-routes
BuildRequires:	dos2unix

Requires:	python-neutron = %{epoch}:%{version}-%{release}
Requires:       python-keystone

Provides:       openstack-neutron = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum < %{epoch}:%{version}-%{release}

%if ! 0%{?usr_only}
Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(preun):  initscripts
Requires(pre):    shadow-utils
%endif

%description
Neutron is a virtual network service for Openstack. Just like OpenStack
Nova provides an API to dynamically request and configure virtual
servers, Neutron provides an API to dynamically request and configure
virtual networks. These networks connect "interfaces" from other
OpenStack services (e.g., virtual NICs from Nova VMs). The Neutron API
supports extensions to provide advanced network capabilities (e.g., QoS,
ACLs, network monitoring, etc.)


%package -n python-neutron
Summary:	Neutron Python libraries
Group:		Applications/System

Provides:       python-neutron = %{epoch}:%{version}-%{release}
Obsoletes:      python-neutron < %{epoch}:%{version}-%{release}
Obsoletes:      python-quantum < %{epoch}:%{version}-%{release}

Requires:	sudo
#for $i in $requires
Requires:	${i}
#end for


%description -n python-neutron
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron Python library.


%package -n openstack-neutron-bigswitch
Summary:	Neutron Big Switch plugin
Group:		Applications/System

Provides:       openstack-neutron-bigswitch = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-bigswitch < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-bigswitch < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-bigswitch
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using the FloodLight Openflow Controller or the Big Switch
Networks Controller.


%package -n openstack-neutron-brocade
Summary:	Neutron Brocade plugin
Group:		Applications/System

Provides:       openstack-neutron-brocade = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-brocade < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-brocade < %{epoch}:%{version}-%{release}


Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-brocade
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using Brocade VCS switches running NOS.


%package -n openstack-neutron-cisco
Summary:	Neutron Cisco plugin
Group:		Applications/System

Provides:       openstack-neutron-cisco = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-cisco < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-cisco < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}
Requires:	python-configobj


%description -n openstack-neutron-cisco
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using Cisco UCS and Nexus.


%package -n openstack-neutron-hyperv
Summary:	Neutron Hyper-V plugin
Group:		Applications/System

Provides:       openstack-neutron-hyperv = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-hyperv < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-hyperv < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-hyperv
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using Microsoft Hyper-V.

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%package -n openstack-neutron-ibm
Summary:        Neutron IBM plugin
Group:          Applications/System

Provides:       openstack-neutron-ibm = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-ibm < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-ibm < %{epoch}:%{version}-%{release}

Requires:       openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-ibm
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using IBM.
#end if

%package -n openstack-neutron-linuxbridge
Summary:	Neutron linuxbridge plugin
Group:		Applications/System

Provides:       openstack-neutron-linuxbridge = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-linuxbridge < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-linuxbridge < %{epoch}:%{version}-%{release}

Requires:	bridge-utils
Requires:	openstack-neutron = %{epoch}:%{version}-%{release}
Requires:	python-pyudev


%description -n openstack-neutron-linuxbridge
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks as VLANs using Linux bridging.


%package -n openstack-neutron-midonet
Summary:	Neutron MidoNet plugin
Group:		Applications/System

Provides:       openstack-neutron-midonet = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-midonet < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-midonet < %{epoch}:%{version}-%{release}


Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-midonet
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using MidoNet from Midokura.


%package -n openstack-neutron-ml2
Summary:	Neutron ML2 plugin
Group:		Applications/System

Provides:       openstack-neutron-ml2 = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-ml2 < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-ml2 < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}
Requires:       python-stevedore >= 0.9


%description -n openstack-neutron-ml2
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains a neutron plugin that allows the use of drivers to
support separately extensible sets of network types and the mechanisms
for accessing those types.


%package -n openstack-neutron-mlnx
Summary:	Neutron Mellanox plugin
Group:		Applications/System

Provides:       openstack-neutron-mlnx = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-mlnx < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-mlnx < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-mlnx
Neutron provides an API to dynamically request and configure virtual
networks.

This plugin implements Quantum v2 APIs with support for Mellanox
embedded switch functionality as part of the VPI (Ethernet/InfiniBand)
HCA.

#if $older_than('2014.1')
%package -n openstack-neutron-nicira
Summary:	Neutron Nicira plugin
Group:		Applications/System

Provides:       openstack-quantum-nicira = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-nicira < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-nicira
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using Nicira NVP.
#end if

#if $newer_than_eq('2014.1')
%package -n openstack-neutron-ofagent
Summary:        Neutron ofagent plugin
Group:          Applications/System

Provides:       openstack-neutron-ofagent = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-ofagent < %{epoch}:%{version}-%{release}

Requires:       openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-ofagent
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using ofagent.
#end if

%package -n openstack-neutron-openvswitch
Summary:	Neutron openvswitch plugin
Group:		Applications/System

Provides:       openstack-neutron-openvswitch = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-openvswitch < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-openvswitch < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}
Requires:	openvswitch


%description -n openstack-neutron-openvswitch
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using Open vSwitch.

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%package -n openstack-neutron-oneconvergence-nvsd
Summary:        Neutron oneconvergence plugin
Group:          Applications/System

Provides:       openstack-neutron-oneconvergence-nvsd = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-oneconvergence-nvsd < %{epoch}:%{version}-%{release}

Requires:       openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-oneconvergence-nvsd
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using oneconvergence nvsd.
#end if

%package -n openstack-neutron-plumgrid
Summary:	Neutron PLUMgrid plugin
Group:		Applications/System

Provides:       openstack-neutron-plumgrid = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-plumgrid < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-plumgrid < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-plumgrid
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using the PLUMgrid platform.


%package -n openstack-neutron-ryu
Summary:	Neutron Ryu plugin
Group:		Applications/System

Provides:       openstack-neutron-ryu = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-ryu < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-ryu < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-ryu
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using the Ryu Network Operating System.


%package -n openstack-neutron-nec
Summary:	Neutron NEC plugin
Group:		Applications/System

Provides:       openstack-neutron-nec = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-nec < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-nec < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-nec
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using the NEC OpenFlow controller.


%package -n openstack-neutron-metaplugin
Summary:	Neutron meta plugin
Group:		Applications/System

Provides:       openstack-neutron-metaplugin = %{epoch}:%{version}-%{release}
Obsoletes:      openstack-neutron-metaplugin < %{epoch}:%{version}-%{release}
Obsoletes:      openstack-quantum-metaplugin < %{epoch}:%{version}-%{release}

Requires:	openstack-neutron = %{epoch}:%{version}-%{release}


%description -n openstack-neutron-metaplugin
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the neutron plugin that implements virtual
networks using multiple other neutron plugins.

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%package -n openstack-neutron-vmware
Summary:       Neutron VMWare NSX support
Group:         Applications/System

Requires:      openstack-neutron = %{version}-%{release}
Provides:      openstack-neutron-nicera = %{version}-%{release}
Obsoletes:     openstack-neutron-nicera < %{version}-%{release}

%description -n openstack-neutron-vmware
Neutron provides an API to dynamically request and configure virtual
networks.

This package adds VMWare NSX support for Neutron,
#end if


%if ! 0%{?no_tests}
%package -n python-%{python_name}-tests
Summary:          Tests for Quantum
Group:            Development/Libraries

Requires:         %{name} = %{epoch}:%{version}-%{release}
Requires:         %{name}-bigswitch = %{epoch}:%{version}-%{release}
Requires:         %{name}-brocade = %{epoch}:%{version}-%{release}
Requires:         %{name}-cisco = %{epoch}:%{version}-%{release}
Requires:         %{name}-hyperv = %{epoch}:%{version}-%{release}
Requires:         %{name}-linuxbridge = %{epoch}:%{version}-%{release}
Requires:         %{name}-midonet = %{epoch}:%{version}-%{release}
Requires:         %{name}-nicira = %{epoch}:%{version}-%{release}
Requires:         %{name}-openvswitch = %{epoch}:%{version}-%{release}
Requires:         %{name}-plumgrid = %{epoch}:%{version}-%{release}
Requires:         %{name}-ryu = %{epoch}:%{version}-%{release}
Requires:         %{name}-nec = %{epoch}:%{version}-%{release}
Requires:         %{name}-metaplugin = %{epoch}:%{version}-%{release}
Requires:         python-%{python_name} = %{epoch}:%{version}-%{release}

# Test requirements:
#for $i in $test_requires
Requires:         ${i}
#end for

%description -n python-%{python_name}-tests
Quantum provides an API to dynamically request and configure virtual
networks.

This package contains unit and functional tests for Quantum, with
simple runner (%{python_name}-make-test-env).
%endif

%prep
%setup -q -n neutron-%{os_version}
#for $idx, $fn in enumerate($patches)
%patch$idx -p1
#end for
#raw

find neutron -name \*.py -exec sed -i '/\/usr\/bin\/env python/d' {} \;

chmod 644 neutron/plugins/cisco/README

# Adjust configuration file content
sed -i 's/debug = True/debug = False/' etc/neutron.conf
sed -i 's/\# auth_strategy = keystone/auth_strategy = keystone/' etc/neutron.conf

# Remove unneeded dependency
sed -i '/setuptools_git/d' setup.py

# let RPM handle deps
sed -i '/setup_requires/d; /install_requires/d; /dependency_links/d' setup.py


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%if ! 0%{?no_tests}
#end raw
#include $part_fn("install_tests.sh")
#raw
%endif

# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/bin
rm -rf %{buildroot}%{python_sitelib}/doc
rm -rf %{buildroot}%{python_sitelib}/tools
rm -f %{buildroot}%{python_sitelib}/neutron/plugins/*/run_tests.*
rm %{buildroot}/usr/etc/init.d/neutron-server

# Install execs
install -p -D -m 755 bin/* %{buildroot}%{_bindir}/

# Move rootwrap files to proper location
install -d -m 755 %{buildroot}%{_datarootdir}/neutron/rootwrap
mv %{buildroot}/usr/etc/neutron/rootwrap.d/*.filters %{buildroot}%{_datarootdir}/neutron/rootwrap

%if ! 0%{?usr_only}
# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron
mv %{buildroot}/usr/etc/neutron/* %{buildroot}%{_sysconfdir}/neutron
chmod 640  %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini

# Configure agents to use neutron-rootwrap
for f in %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini %{buildroot}%{_sysconfdir}/neutron/*_agent.ini; do
    sed -i 's/^root_helper.*/root_helper = sudo neutron-rootwrap \/etc\/neutron\/rootwrap.conf/g' $f
done

# Configure neutron-dhcp-agent state_path
sed -i 's/state_path = \/opt\/stack\/data/state_path = \/var\/lib\/neutron/' %{buildroot}%{_sysconfdir}/neutron/dhcp_agent.ini

# Install logrotate
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-neutron

# Install sudoers
install -p -D -m 440 %{SOURCE2} %{buildroot}%{_sysconfdir}/sudoers.d/neutron

# Install sysv init scripts
install -p -D -m 755 %{SOURCE10} %{buildroot}%{_initrddir}/%{daemon_prefix}-server
install -p -D -m 755 %{SOURCE11} %{buildroot}%{_initrddir}/%{daemon_prefix}-linuxbridge-agent
install -p -D -m 755 %{SOURCE12} %{buildroot}%{_initrddir}/%{daemon_prefix}-openvswitch-agent
install -p -D -m 755 %{SOURCE13} %{buildroot}%{_initrddir}/%{daemon_prefix}-ryu-agent
install -p -D -m 755 %{SOURCE14} %{buildroot}%{_initrddir}/%{daemon_prefix}-nec-agent
install -p -D -m 755 %{SOURCE15} %{buildroot}%{_initrddir}/%{daemon_prefix}-dhcp-agent
install -p -D -m 755 %{SOURCE16} %{buildroot}%{_initrddir}/%{daemon_prefix}-l3-agent
install -p -D -m 755 %{SOURCE17} %{buildroot}%{_initrddir}/%{daemon_prefix}-ovs-cleanup
install -p -D -m 755 %{SOURCE18} %{buildroot}%{_initrddir}/%{daemon_prefix}-hyperv-agent
install -p -D -m 755 %{SOURCE19} %{buildroot}%{_initrddir}/%{daemon_prefix}-rpc-zmq-receiver
install -p -D -m 755 %{SOURCE20} %{buildroot}%{_initrddir}/%{daemon_prefix}-metadata-agent

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/neutron
install -d -m 755 %{buildroot}%{_localstatedir}/log/neutron
install -d -m 755 %{buildroot}%{_localstatedir}/lock/neutron
install -d -m 755 %{buildroot}%{_localstatedir}/run/neutron

# Install version info file
cat > %{buildroot}%{_sysconfdir}/neutron/release <<EOF
[Neutron]
vendor = OpenStack LLC
product = OpenStack Neutron
package = %{release}
EOF
%else
rm -rf %{buildroot}/usr/etc/
%endif

%clean
rm -rf %{buildroot}


%if ! 0%{?usr_only}
%pre
getent group neutron >/dev/null || groupadd -r neutron
getent passwd neutron >/dev/null || \
useradd -r -g neutron -d %{_sharedstatedir}/neutron -s /sbin/nologin \
-c "OpenStack Neutron Daemons" neutron
exit 0

# Do not autostart daemons in %post since they are not configured yet
#end raw

#set $daemon_map = {"": ["server", "dhcp-agent", "l3-agent"], "linuxbridge": ["linuxbridge-agent"], "openvswitch": ["openvswitch-agent", "ovs-cleanup"], "ryu": ["ryu-agent"], "nec": ["nec-agent"]}
#for $key, $value in $daemon_map.iteritems()
#set $daemon_list = " ".join($value) if $value else $key
%preun $key
if [ \$1 -eq 0 ] ; then
    for svc in $daemon_list; do
        /sbin/service %{daemon_prefix}-\${svc} stop &>/dev/null
        /sbin/chkconfig --del %{daemon_prefix}-\${svc}
    done
    exit 0
fi

%postun $key
if [ \$1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in $daemon_list; do
        /sbin/service %{daemon_prefix}-\${svc} condrestart &>/dev/null
    done
    exit 0
fi

#end for
%endif

%files
%doc README* LICENSE HACKING* ChangeLog AUTHORS
%{_bindir}/*-db-manage
%{_bindir}/*-debug
%{_bindir}/*-dhcp-agent
%{_bindir}/*-l3-agent
%{_bindir}/*-lbaas-agent
%{_bindir}/*-metadata-agent
%{_bindir}/*-metering-agent
%{_bindir}/*-netns-cleanup
%{_bindir}/*-ns-metadata-proxy
%{_bindir}/*-rootwrap
%{_bindir}/*-rpc-zmq-receiver
%{_bindir}/*-server
%{_bindir}/*-usage-audit
%{_bindir}/*-vpn-agent

%{_datarootdir}/neutron
%exclude %{_datarootdir}/neutron/rootwrap/linuxbridge-plugin.filters
%exclude %{_datarootdir}/neutron/rootwrap/openvswitch-plugin.filters
%exclude %{_datarootdir}/neutron/rootwrap/ryu-plugin.filters
%exclude %{_datarootdir}/neutron/rootwrap/nec-plugin.filters

%if ! 0%{?usr_only}
%{_initrddir}/%{daemon_prefix}-server
%{_initrddir}/%{daemon_prefix}-dhcp-agent
%{_initrddir}/%{daemon_prefix}-l3-agent
%{_initrddir}/%{daemon_prefix}-metadata-agent
%{_initrddir}/%{daemon_prefix}-rpc-zmq-receiver
%dir %{_sysconfdir}/neutron
%{_sysconfdir}/neutron/release
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/policy.json
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/neutron.conf
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/*.ini
%config(noreplace) %{_sysconfdir}/neutron/rootwrap.conf
%dir %{_sysconfdir}/neutron/plugins
%config(noreplace) %{_sysconfdir}/logrotate.d/*
%config(noreplace) %{_sysconfdir}/sudoers.d/neutron
%dir %attr(0755, neutron, neutron) %{_sharedstatedir}/neutron
%dir %attr(0755, neutron, neutron) %{_localstatedir}/log/neutron
%dir %attr(0755, neutron, neutron) %{_localstatedir}/lock/neutron
%dir %attr(0755, neutron, neutron) %{_localstatedir}/run/neutron
%endif

%files -n python-neutron
%doc LICENSE
%{python_sitelib}/neutron
%{python_sitelib}/quantum
%exclude %{python_sitelib}/neutron/tests
%exclude %{python_sitelib}/neutron/plugins/bigswitch
%exclude %{python_sitelib}/neutron/plugins/brocade
%exclude %{python_sitelib}/neutron/plugins/cisco
%exclude %{python_sitelib}/neutron/plugins/hyperv
%exclude %{python_sitelib}/neutron/plugins/linuxbridge
%exclude %{python_sitelib}/neutron/plugins/metaplugin
%exclude %{python_sitelib}/neutron/plugins/midonet
%exclude %{python_sitelib}/neutron/plugins/nec
%exclude %{python_sitelib}/neutron/plugins/ml2
%exclude %{python_sitelib}/neutron/plugins/mlnx
%exclude %{python_sitelib}/neutron/plugins/nicira
%exclude %{python_sitelib}/neutron/plugins/openvswitch
%exclude %{python_sitelib}/neutron/plugins/plumgrid
%exclude %{python_sitelib}/neutron/plugins/ryu
#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%exclude %{python_sitelib}/neutron/plugins/ibm
%exclude %{python_sitelib}/neutron/plugins/ofagent
%exclude %{python_sitelib}/neutron/plugins/oneconvergence
%exclude %{python_sitelib}/neutron/plugins/vmware
#end if

%{python_sitelib}/neutron-*.egg-info


%files -n openstack-neutron-bigswitch
%doc LICENSE
%doc neutron/plugins/bigswitch/README
#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%doc %{_sysconfdir}/neutron/plugins/bigswitch/README
%{_bindir}/neutron-restproxy-agent
#end if
%{python_sitelib}/neutron/plugins/bigswitch
%exclude %{python_sitelib}/neutron/plugins/bigswitch/tests

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/bigswitch
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/bigswitch/*.ini
%endif


%files -n openstack-neutron-brocade
%doc LICENSE
%doc neutron/plugins/brocade/README.md
%{python_sitelib}/neutron/plugins/brocade
%exclude %{python_sitelib}/neutron/plugins/brocade/tests

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/brocade
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/brocade/*.ini
%endif


%files -n openstack-neutron-cisco
%doc LICENSE
%doc neutron/plugins/cisco/README
%{python_sitelib}/neutron/plugins/cisco

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/cisco
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/cisco/*.ini
%endif


%files -n openstack-neutron-hyperv
%doc LICENSE
%{_bindir}/*-hyperv-agent
%{python_sitelib}/neutron/plugins/hyperv
%exclude %{python_sitelib}/neutron/plugins/hyperv/agent

%if ! 0%{?usr_only}
%{_initrddir}/%{daemon_prefix}-hyperv-agent
%dir %{_sysconfdir}/neutron/plugins/hyperv
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/hyperv/*.ini
%endif

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%doc LICENSE
%files -n openstack-neutron-ibm
%doc neutron/plugins/ibm/README
%{_bindir}/*-ibm-agent
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/ibm/*.ini
%{python_sitelib}/neutron/plugins/ibm

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/ibm
%endif
#end if

%files -n openstack-neutron-linuxbridge
%doc LICENSE
%doc neutron/plugins/linuxbridge/README
%{_bindir}/*-linuxbridge-agent
%{python_sitelib}/neutron/plugins/linuxbridge
%{_datarootdir}/neutron/rootwrap/linuxbridge-plugin.filters

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/linuxbridge
%{_initrddir}/%{daemon_prefix}-linuxbridge-agent
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/linuxbridge/*.ini
%endif


%files -n openstack-neutron-midonet
%doc LICENSE
%{python_sitelib}/neutron/plugins/midonet

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/midonet
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/midonet/*.ini
%endif

%files -n openstack-neutron-ml2
%doc LICENSE
%doc neutron/plugins/ml2/README
%{python_sitelib}/neutron/plugins/ml2

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/ml2
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/ml2/*.ini
%endif

%files -n openstack-neutron-mlnx
%doc LICENSE
%doc neutron/plugins/mlnx/README
%{_bindir}/*-mlnx-agent
%{python_sitelib}/neutron/plugins/mlnx

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/mlnx
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/mlnx/*.ini
%endif

#if $older_than('2014.1')
%files -n openstack-neutron-nicira
%doc LICENSE
%doc neutron/plugins/nicira/README
%{_bindir}/*-check-nvp-config
%{python_sitelib}/neutron/plugins/nicira
#end if

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/nicira
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/nicira/*.ini
%endif

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%files -n openstack-neutron-ofagent
%doc LICENSE
%{_bindir}/*-ofagent-agent
%doc neutron/plugins/ofagent/README
%{python_sitelib}/neutron/plugins/ofagent
#end if

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%files -n openstack-neutron-oneconvergence-nvsd
%doc LICENSE
%doc neutron/plugins/oneconvergence/README
%{_bindir}/*-nvsd-agent
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/oneconvergence/*.ini
%{python_sitelib}/neutron/plugins/oneconvergence
#end if

%files -n openstack-neutron-openvswitch
%doc LICENSE
%doc neutron/plugins/openvswitch/README
%{_bindir}/*-openvswitch-agent
%{_bindir}/*-ovs-cleanup
%{_bindir}/*-rootwrap-xen-dom0
%{_datarootdir}/neutron/rootwrap/openvswitch-plugin.filters
%{python_sitelib}/neutron/plugins/openvswitch

%if ! 0%{?usr_only}
%{_initrddir}/%{daemon_prefix}-openvswitch-agent
%{_initrddir}/%{daemon_prefix}-ovs-cleanup
%dir %{_sysconfdir}/neutron/plugins/openvswitch
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/openvswitch/*.ini
%endif

%files -n openstack-neutron-plumgrid
%doc LICENSE
%doc neutron/plugins/plumgrid/README
%{python_sitelib}/neutron/plugins/plumgrid

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/plumgrid
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/plumgrid/*.ini
%endif

%files -n openstack-neutron-ryu
%doc LICENSE
%doc neutron/plugins/ryu/README
%{_bindir}/*-ryu-agent
%{python_sitelib}/neutron/plugins/ryu
%{_datarootdir}/neutron/rootwrap/ryu-plugin.filters

%if ! 0%{?usr_only}
%{_initrddir}/%{daemon_prefix}-ryu-agent
%dir %{_sysconfdir}/neutron/plugins/ryu
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/ryu/*.ini
%endif

%files -n openstack-neutron-nec
%doc LICENSE
%doc neutron/plugins/nec/README
%{_bindir}/*-nec-agent
%{python_sitelib}/neutron/plugins/nec
%{_datarootdir}/neutron/rootwrap/nec-plugin.filters

%if ! 0%{?usr_only}
%{_initrddir}/%{daemon_prefix}-nec-agent
%dir %{_sysconfdir}/neutron/plugins/nec
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/nec/*.ini
%endif

#if $newer_than_eq('2014.1.dev146.g79fbeb7')
%files -n openstack-neutron-vmware
%doc LICENSE
%{_bindir}/neutron*nsx-*
%{_bindir}/*-check-nvp-config
%dir %{_sysconfdir}/neutron/plugins/vmware
%dir %{_sysconfdir}/neutron/plugins/nicira

%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/vmware/*.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/nicira/*.ini
%{python_sitelib}/neutron/plugins/vmware
#end if

%files -n openstack-neutron-metaplugin
%doc LICENSE
%doc neutron/plugins/metaplugin/README
%{python_sitelib}/neutron/plugins/metaplugin

%if ! 0%{?usr_only}
%dir %{_sysconfdir}/neutron/plugins/metaplugin
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/metaplugin/*.ini
%endif

%if ! 0%{?no_tests}
%files -n python-%{python_name}-tests
%{tests_data_dir}
%{_bindir}/%{python_name}-make-test-env
%endif

%changelog
