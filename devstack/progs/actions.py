# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
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
#    under the License..

import time

from devstack import date
from devstack import env_rc
from devstack import exceptions as excp
from devstack import log as logging
from devstack import settings
from devstack import shell as sh
from devstack import utils

from devstack.packaging import apt
from devstack.packaging import yum

from devstack.progs import common

LOG = logging.getLogger("devstack.progs.actions")

# This map controls which distro has
# which package management class
_PKGR_MAP = {
    settings.UBUNTU11: apt.AptPackager,
    settings.RHEL6: yum.YumPackager,
    settings.FEDORA16: yum.YumPackager,
}

# This is used to map an action to a useful string for
# the welcome display
_WELCOME_MAP = {
    settings.INSTALL: "INSTALLER",
    settings.UNINSTALL: "UNINSTALLER",
    settings.START: "STARTER",
    settings.STOP: "STOPPER",
}

# For actions in this list we will reverse the component order
_REVERSE_ACTIONS = [settings.UNINSTALL, settings.STOP]

# These will not automatically stop when uninstalled since it seems to break there password reset.
_NO_AUTO_STOP = [settings.DB, settings.RABBIT]

# For these actions we will attempt to make an rc file if it does not exist
_RC_FILE_MAKE_ACTIONS = [settings.INSTALL, settings.START]
_RC_FILE = sh.abspth(settings.OSRC_FN)

# For these actions we will ensure the preq occurs first
_DEP_ACTIONS = {
    settings.START: {
        'check_func': (lambda instance, component_name:
                        (not instance.is_installed())),
        'dependent_action': settings.INSTALL,
    },
    settings.UNINSTALL: {
        'check_func': (lambda instance, component_name:
                        (instance.is_started() and component_name not in _NO_AUTO_STOP)),
        'dependent_action': settings.STOP,
    },
}


def _clean_action(action):
    if action is None:
        return None
    action = action.strip().lower()
    if not (action in settings.ACTIONS):
        return None
    return action


def _get_pkg_manager(distro, keep_packages):
    cls = _PKGR_MAP.get(distro)
    if not cls:
        msg = "No package manager found for distro %s!" % (distro)
        raise excp.StackException(msg)
    return cls(distro, keep_packages)


def _pre_run(action_name, root_dir, pkg_manager, config, component_order, instances):
    loaded_env = False
    rc_fn = _RC_FILE
    try:
        if sh.isfile(rc_fn):
            LOG.info("Attempting to load rc file at [%s] which has your environment settings." % (rc_fn))
            am_loaded = env_rc.load_local_rc(rc_fn)
            loaded_env = True
            LOG.info("Loaded [%s] settings from rc file [%s]" % (am_loaded, rc_fn))
    except IOError:
        LOG.warn('Error reading rc file located at [%s]. Skipping loading it.' % (rc_fn))
    if action_name == settings.INSTALL:
        if root_dir:
            sh.mkdir(root_dir)
    LOG.info("Verifying that the components are ready to rock-n-roll.")
    all_instances = instances[0]
    prerequisite_instances = instances[1]
    for component in component_order:
        base_inst = all_instances.get(component)
        if component in prerequisite_instances:
            (_, pre_inst) = prerequisite_instances[component]
            pre_inst.verify()
        if base_inst:
            base_inst.verify()
    LOG.info("Warming up your component configurations (ie so you won't be prompted later)")
    for component in component_order:
        base_inst = all_instances.get(component)
        if component in prerequisite_instances:
            (_, pre_inst) = prerequisite_instances[component]
            pre_inst.warm_configs()
        if base_inst:
            base_inst.warm_configs()
    if action_name in _RC_FILE_MAKE_ACTIONS and not loaded_env:
        _gen_localrc(config, rc_fn)


def _post_run(action_name, root_dir, config, components, time_taken, results):
    LOG.info("It took (%s) to complete action [%s]" % (common.format_secs_taken(time_taken), action_name))
    if results:
        LOG.info('Check [%s] for traces of what happened.' % ", ".join(results))
    #show any configs read/touched/used...
    _print_cfgs(config, action_name)
    #try to remove the root - ok if this fails
    if action_name == settings.UNINSTALL:
        if root_dir:
            sh.rmdir(root_dir)


def _print_cfgs(config_obj, action):

    #this will make the items nice and pretty
    def item_format(key, value):
        return "\t%s=%s" % (str(key), str(value))

    def map_print(mp):
        for key in sorted(mp.keys()):
            value = mp.get(key)
            LOG.info(item_format(key, value))

    #now make it pretty
    passwords_gotten = config_obj.pws
    full_cfgs = config_obj.configs_fetched
    db_dsns = config_obj.db_dsns
    if passwords_gotten or full_cfgs or db_dsns:
        LOG.info("After action [%s] your settings which were created or read are:" % (action))
        if passwords_gotten:
            LOG.info("Passwords:")
            map_print(passwords_gotten)
        if full_cfgs:
            filtered = dict((k, v) for (k, v) in full_cfgs.items() if k not in passwords_gotten)
            if filtered:
                LOG.info("Configs:")
                map_print(filtered)
        if db_dsns:
            LOG.info("Data source names:")
            map_print(db_dsns)


def _install(component_name, instance, force):
    LOG.info("Downloading %s." % (component_name))
    am_downloaded = instance.download()
    LOG.info("Performed %s downloads." % (am_downloaded))
    LOG.info("Configuring %s." % (component_name))
    am_configured = instance.configure()
    LOG.info("Configured %s items." % (am_configured))
    LOG.info("Pre-installing %s." % (component_name))
    instance.pre_install()
    LOG.info("Installing %s." % (component_name))
    trace = instance.install()
    LOG.info("Post-installing %s." % (component_name))
    instance.post_install()
    if trace:
        LOG.info("Finished install of %s - check %s for traces of what happened." % (component_name, trace))
    else:
        LOG.info("Finished install of %s" % (component_name))
    return trace


def _stop(component_name, instance, force):
    try:
        LOG.info("Stopping %s." % (component_name))
        stop_amount = instance.stop()
        LOG.info("Stopped %s items." % (stop_amount))
        LOG.info("Finished stop of %s." % (component_name))
    except (excp.NoTraceException, excp.ProcessExecutionError) as e:
        if force:
            LOG.debug("Skipping exception [%s]" % (e))
        else:
            raise


def _start(component_name, instance, force):
    LOG.info("Pre-starting %s." % (component_name))
    instance.pre_start()
    LOG.info("Starting %s." % (component_name))
    start_info = instance.start()
    LOG.info("Post-starting %s." % (component_name))
    instance.post_start()
    #TODO clean this up.
    if type(start_info) == list:
        LOG.info("Check [%s] for traces of what happened." % (", ".join(start_info)))
    elif type(start_info) == int:
        LOG.info("Started %s applications." % (start_info))
        start_info = None
    LOG.info("Finished start of %s." % (component_name))
    return start_info


def _uninstall(component_name, instance, force):
    try:
        LOG.info("Unconfiguring %s." % (component_name))
        instance.unconfigure()
        LOG.info("Pre-uninstalling %s." % (component_name))
        instance.pre_uninstall()
        LOG.info("Uninstalling %s." % (component_name))
        instance.uninstall()
        LOG.info("Post-uninstalling %s." % (component_name))
        instance.post_uninstall()
    except (excp.NoTraceException) as e:
        if force:
            LOG.debug("Skipping exception [%s]" % (e))
        else:
            raise


def _instanciate_components(action_name, components, distro, pkg_manager, config, root_dir):
    all_instances = dict()
    prerequisite_instances = dict()

    for component in components.keys():
        base_cls = common.get_action_cls(action_name, component, distro)
        base_instance = base_cls(instances=all_instances,
                              distro=distro,
                              packager=pkg_manager,
                              config=config,
                              root=root_dir,
                              opts=components.get(component, list()))
        all_instances[component] = base_instance

        preq_info = _DEP_ACTIONS.get(action_name)
        if preq_info:
            checker = preq_info['check_func']
            if checker(base_instance, component):
                preq_action_name = preq_info['dependent_action']
                preq_action_cls = common.get_action_cls(preq_action_name, component, distro)
                preq_instance = preq_action_cls(instances=all_instances,
                              distro=distro,
                              packager=pkg_manager,
                              config=config,
                              root=root_dir,
                              opts=components.get(component, list()))
                prerequisite_instances[component] = (preq_action_name, preq_instance)

    return (all_instances, prerequisite_instances)


def _gen_localrc(config, fn):
    LOG.info("Generating a file at [%s] that will contain your environment settings." % (fn))
    env_rc.generate_local_rc(fn, config)


def _run_components(action_name, component_order, components, distro, root_dir, program_args):
    LOG.info("Will run action [%s] using root directory [%s]" % (action_name, root_dir))
    LOG.info("In the following order: %s" % ("->".join(component_order)))
    non_components = set(components.keys()).difference(set(component_order))
    if non_components:
        LOG.info("Using reference components (%s)" % (", ".join(sorted(non_components))))
    #get the package manager + config
    pkg_manager = _get_pkg_manager(distro, program_args.get('keep_packages', True))
    config = common.get_config()
    #form the active instances (this includes ones we won't use)
    (all_instances, prerequisite_instances) = _instanciate_components(action_name,
                                                                      components,
                                                                      distro,
                                                                      pkg_manager,
                                                                      config,
                                                                      root_dir)
    #run anything before it gets going...
    _pre_run(action_name, root_dir=root_dir, pkg_manager=pkg_manager,
              config=config, component_order=component_order,
              instances=(all_instances, prerequisite_instances))
    LOG.info("Activating components required to complete action %s." % (action_name))
    action_functor_map = {
        settings.START: _start,
        settings.INSTALL: _install,
        settings.UNINSTALL: _uninstall,
        settings.STOP: _stop,
    }
    start_time = time.time()
    results = list()
    force = program_args.get('force', False)
    #activate all preqs first
    for component in component_order:
        if component in prerequisite_instances:
            (preq_action, preq_instance) = prerequisite_instances[component]
            LOG.info("Having to activate prerequisite for component %s of action type %s." % (component, preq_action))
            preq_func = action_functor_map[preq_action]
            preq_result = preq_func(component, preq_instance, force)
            if preq_result is None:
                pass
            elif type(preq_result) == list:
                results.extend(preq_result)
            else:
                results.append(str(preq_result))
    #now do main actions
    for component in component_order:
        instance = all_instances[component]
        main_functor = action_functor_map[action_name]
        main_result = main_functor(component, instance, force)
        if main_result is None:
            pass
        elif type(main_result) == list:
            results.extend(main_result)
        else:
            results.append(str(main_result))
    end_time = time.time()
    #any post run actions go now
    _post_run(action_name, root_dir=root_dir,
              config=config, components=components.keys(),
              time_taken=(end_time - start_time), results=results)


def _run_action(args):
    #ensure os/distro is known
    (distro, platform) = utils.determine_distro()
    if distro is None:
        print("Unsupported platform " + utils.color_text(platform, "red") + "!")
        return False
    #extract which components to run
    defaulted_components = False
    components = utils.parse_components(args.pop("components"))
    if not components:
        defaulted_components = True
        components = common.get_default_components(distro)
    #ensure the action is valid
    action = _clean_action(args.pop("action"))
    if not action:
        print(utils.color_text("No valid action specified!", "red"))
        return False
    #ensure we have a root directory
    rootdir = args.pop("dir")
    if rootdir is None:
        print(utils.color_text("No root directory specified!", "red"))
        return False
    #start it
    (rep, maxlen) = utils.welcome(_WELCOME_MAP.get(action))
    header = utils.center_text("Action Runner", rep, maxlen)
    print(header)
    #here on out should be using the logger
    if not defaulted_components:
        LOG.info("Activating components [%s]" % (", ".join(sorted(components.keys()))))
    else:
        LOG.info("Activating default components [%s]" % (", ".join(sorted(components.keys()))))
    #need to figure out dependencies for components (if any)
    ignore_deps = args.pop('ignore_deps', False)
    component_order = None
    if not ignore_deps:
        all_components_deps = common.get_components_deps(action, components, distro, rootdir)
        component_diff = set(all_components_deps.keys()).difference(components.keys())
        if component_diff:
            LOG.info("Having to activate dependent components: [%s]" \
                         % (", ".join(sorted(component_diff))))
            for new_component in component_diff:
                components[new_component] = list()
        component_order = utils.get_components_order(all_components_deps)
    else:
        component_order = components.keys()
    #reverse them so that we stop in the reverse order
    #and that we uninstall in the reverse order which seems to make sense
    if action in _REVERSE_ACTIONS:
        component_order.reverse()
    #add in any that will just be referenced but which will not actually do anything (ie the action will not be applied to these)
    ref_components = utils.parse_components(args.pop("ref_components"))
    for c in ref_components.keys():
        if c not in components:
            components[c] = ref_components.get(c)
    #now do it!
    LOG.info("Starting action [%s] on %s for distro [%s]" % (action, date.rcf8222date(), distro))
    _run_components(action, component_order, components, distro, rootdir, args)
    LOG.info("Finished action [%s] on %s" % (action, date.rcf8222date()))
    return True


def run(args):
    return _run_action(args)
