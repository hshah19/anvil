# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from devstack import component as comp
from devstack import constants as co
from devstack import log as logging
from devstack import shell as sh
from devstack import utils
from devstack.components import nova_conf as nc

LOG = logging.getLogger("devstack.components.nova")

API_CONF = "nova.conf"
PASTE_CONF = 'nova-api-paste.ini'
CONFIGS = [API_CONF]

DB_NAME = "nova"
BIN_DIR = 'bin'
TYPE = co.NOVA
QUANTUM_MANAGER = 'nova.network.quantum.manager.QuantumManager'
NET_MAN_TEMPL = 'nova.network.manager.%s'
IMG_SVC = 'nova.image.glance.GlanceImageService'

QUANTUM_OPENSWITCH_OPS = [
    {
      'libvirt_vif_type': ['ethernet'],
      'libvirt_vif_driver': ['nova.virt.libvirt.vif.LibvirtOpenVswitchDriver'],
      'linuxnet_interface_driver': ['nova.network.linux_net.LinuxOVSInterfaceDriver'],
      'quantum_use_dhcp': [],
    }
]


class NovaUninstaller(comp.PythonUninstallComponent):
    def __init__(self, *args, **kargs):
        comp.PythonUninstallComponent.__init__(self, TYPE, *args, **kargs)
        #self.cfgdir = joinpths(self.appdir, CONFIG_ACTUAL_DIR)

class NovaConfigurator():
    def __init__(self, cfg, active_components):
        self.cfg = cfg
        self.active_components = active_components

    def _getbool(self, name):
        return self.cfg.getboolean('nova', name)
        
    def _getstr(self, name):
        return self.cfg.get('nova', name)

    def configure(self, dirs):
        
        #TODO split up into sections??
        
        nova_conf = nc.NovaConf()
        hostip = utils.get_host_ip()
        
        #verbose on?
        if(self._getbool('verbose')):
            nova_conf.add_simple('verbose')

        #allow the admin api?
        if(self._getbool('allow_admin_api')):
            nova_conf.add_simple('allow_admin_api')

        #which sheculder do u want
        nova_conf.add('scheduler_driver', self._getstr('scheduler'))

        #??? 
        nova_conf.add('dhcpbridge_flagfile', utils.joinpths(dirs.get('bin'), API_CONF))

        #whats the network fixed range?
        nova_conf.add('fixed_range', self._getstr('fixed_range'))

        if(co.QUANTUM in self.active_components):
            #setup quantum config
            nova_conf.add('network_manager', QUANTUM_MANAGER)
            nova_conf.add('quantum_connection_host', self.cfg.get('quantum', 'q_host'))
            nova_conf.add('quantum_connection_port', self.cfg.get('quantum', 'q_port'))
            # TODO
            #if ('q-svc' in self.othercomponents and
            #   self.cfg.get('quantum', 'q_plugin') == 'openvswitch'):
            #   self.lines.extend(QUANTUM_OPENSWITCH_OPS)
        else:
            nova_conf.add('network_manager', NET_MAN_TEMPL % (self._getstr('network_manager')))

        # TODO
        #       if ('n-vol' in self.othercomponents):
        #   self._resolve('--volume_group=', 'nova', 'volume_group')
        #   self._resolve('--volume_name_template=',
        #                 'nova', 'volume_name_prefix', '%08x')
        #   self._add('--iscsi_helper=tgtadm')

        nova_conf.add('my_ip', hostip)

        # The value for vlan_interface may default to the the current value
        # of public_interface. We'll grab the value and keep it handy.
        public_interface = self._getstr('public_interface')
        vlan_interface = self._getstr('vlan_interface')
        if(not vlan_interface):
            vlan_interface = public_interface
        nova_conf.add('public_interface', public_interface)
        nova_conf.add('vlan_interface', vlan_interface)


        nova_conf.add('sql_connection', self.cfg.get_dbdsn('nova'))
        nova_conf.add('libvirt_type', self._getstr('libvirt_type'))

        instance_template = self._getstr('instance_name_prefix') + '%08x';
        nova_conf.add('instance_name_template', instance_template)

        if(co.OPENSTACK_X in self.active_components):
            nova_conf.add('osapi_compute_extension', 'nova.api.openstack.compute.contrib.standard_extensions')
            nova_conf.add('osapi_compute_extension', 'extensions.admin.Admin')

        # TODO
        #      if ('n-vnc' in self.othercomponents):
        #  vncproxy_url = self.cfg.get("nova", "vncproxy_url")
        #  if (not vncproxy_url):
        #      vncproxy_url = 'http://' + hostip + ':6080'
        #  self._add('--vncproxy_url=' + vncproxy_url)
        #  self._add('vncproxy_wwwroot=' + nova_dir + '/')
        # 

        # TODO is this right?
        nova_conf.add('api_paste_config', utils.joinpths(dirs.get('bin'), PASTE_CONF))

        nova_conf.add('image_service', IMG_SVC)

        ec2_dmz_host = self._getstr('ec2_dmz_host')
        if(not ec2_dmz_host):
            ec2_dmz_host = utils.get_host_ip()

        nova_conf.add('ec2_dmz_host', ec2_dmz_host)

        nova_conf.add('rabbit_host', self.cfg.get('default', 'rabbit_host'))
        nova_conf.add('rabbit_password', self.cfg.getpw("passwords", "rabbit"))

        glance_svr = "%s:9292" % (hostip)
        nova_conf.add('glance_api_servers', glance_svr)

        nova_conf.add_simple('force_dhcp_release')

        instances_path = self._getstr('instances_path')
        if(instances_path):
            nova_conf.add('instances_path', instances_path)

        if(self._getbool('multi_host')):
            nova_conf.add_simple('multi_host')
            nova_conf.add_simple('send_arp_for_ha')

        if(self.cfg.getboolean('default', 'syslog')):
            nova_conf.add_simple('use_syslog')

        virt_driver = self._getstr('virt_driver')
        self._configure_virt_driver(virt_driver, nova_conf)

        #now make it
        complete_file = nova_conf.generate()

        #add any extra flags in?
        extra_flags = self._getstr('extra_flags')
        if(extra_flags and len(extra_flags)):
            full_file = [complete_file, extra_flags]
            complete_file = utils.joinlinesep(*full_file)

        return complete_file
        
    #configures any virt driver settings
    def _configure_virt_driver(self, driver, nova_conf):
        if(not driver):
            return
        drive_canon = driver.lower().strip()
        if(drive_canon == 'xenserver'):
            nova_conf.add('connection_type', 'xenapi')
            nova_conf.add('xenapi_connection_url', 'http://169.254.0.1')
            nova_conf.add('xenapi_connection_username', 'root')
            # TODO, check that this is the right way to get the password
            nova_conf.add('xenapi_connection_password', self.cfg.getpw("passwords", "xenapi"))
            nova_conf.add_simple('noflat_injected')
            nova_conf.add('flat_interface', 'eth1')
            nova_conf.add('flat_network_bridge', 'xapi1')
        else:
            nova_conf.add('flat_network_bridge', self._getstr('flat_network_bridge'))
            nova_conf.add('flat_interface', self._getstr('flat_interface'))


class NovaInstaller(comp.PythonInstallComponent):
    def __init__(self, *args, **kargs):
        comp.PythonInstallComponent.__init__(self, TYPE, *args, **kargs)
        self.git_repo = self.cfg.get("git", "nova_repo")
        self.git_branch = self.cfg.get("git", "nova_branch")
        self.bindir = utils.joinpths(self.appdir, BIN_DIR)

    def _get_download_location(self):
        places = comp.PythonInstallComponent._get_download_locations(self)
        places.append({
            'uri': self.git_repo,
            'branch': self.git_branch,
        })
        return places
    
    def _generate_nova_conf(self):
        LOG.debug("Generating dynamic content for nova.conf")
        dirs = dict()
        dirs['app'] = self.appdir
        dirs['cfg'] = self.cfgdir
        dirs['bin'] = self.bindir
        conf_gen = NovaConfigurator(self.cfg, self.all_components, dirs)
        nova_conf = conf_gen.configure(dirs)
        tgtfn = self._get_target_config_name(API_CONF)
        sh.write_file(tgtfn, nova_conf)
        return 1

    def _configure_files(self):
        return self._generate_nova_conf()


class NovaRuntime(comp.PythonRuntime):
    def __init__(self, *args, **kargs):
        comp.PythonRuntime.__init__(self, TYPE, *args, **kargs)
