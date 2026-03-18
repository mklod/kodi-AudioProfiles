
import json
import os
import sys
import xbmc
import xbmcgui
from resources.lib import apdialog
from resources.lib.fileops import *


class Profiles:

    def __init__(self, settings, lw, auto=False):
        """Handles audio profile switching."""
        self.LW = lw
        self.SETTINGS = settings
        self.AUTO = auto
        self.SNAME = {1: self.SETTINGS['name1'],
                      2: self.SETTINGS['name2'],
                      3: self.SETTINGS['name3'],
                      4: self.SETTINGS['name4'],
                      5: self.SETTINGS['name5'],
                      6: self.SETTINGS['name6'],
                      7: self.SETTINGS['name7'],
                      8: self.SETTINGS['name8'],
                      9: self.SETTINGS['name9'],
                      10: self.SETTINGS['name10']}
        self.SPROFILE = {1: self.SETTINGS['profile1'],
                         2: self.SETTINGS['profile2'],
                         3: self.SETTINGS['profile3'],
                         4: self.SETTINGS['profile4'],
                         5: self.SETTINGS['profile5'],
                         6: self.SETTINGS['profile6'],
                         7: self.SETTINGS['profile7'],
                         8: self.SETTINGS['profile8'],
                         9: self.SETTINGS['profile9'],
                         10: self.SETTINGS['profile10']}
        self.APROFILE = []
        self.CECCOMMANDS = ['', 'CECActivateSource',
                            'CECStandby', 'CECToggleState']
        self.ENABLEDPROFILES = self._get_enabled_profiles()
        self.KODIPLAYER = xbmc.Player()
        self.DIALOG = xbmcgui.Dialog()
        self.NOTIFYTIME = self.SETTINGS['notify_time'] * 1000
        self.DISPLAYNOTIFICATION = self.SETTINGS['notify']
        success, loglines = checkPath(
            os.path.join(self.SETTINGS['ADDONDATAPATH'], ''))
        self.LW.log(loglines)

    def changeProfile(self, mode):
        if True not in self.SPROFILE.values():
            self._notification(self.SETTINGS['ADDONLANGUAGE'](
                32105), self.SETTINGS['notify_maintenance'])
            self.SETTINGS['ADDON'].openSettings()
        if mode is False:
            self._save()
            return
        if mode == 'popup':
            force_dialog = not self.KODIPLAYER.isPlaying()
            dialog_return, loglines = apdialog.Dialog().start(self.SETTINGS, title=self.SETTINGS['ADDONLANGUAGE'](32106),
                                                              buttons=self.ENABLEDPROFILES[1], force_dialog=force_dialog)
            self.LW.log(loglines)
            if dialog_return is not None:
                self._profile(str(self.ENABLEDPROFILES[0][dialog_return]))
            return dialog_return
        if int(mode) <= 10:
            if self._check(mode) is False:
                return
            if mode == '0':
                self._toggle(mode)
            else:
                self._profile(mode)
            return
        self.LW.log(['Wrong argument used - use like RunScript("%s,x") x (x is the number of the profile)' %
                    self.SETTINGS['ADDONNAME']], xbmc.LOGERROR)

    def _check(self, mode):
        if mode != '0' and not self.SPROFILE[int(mode)]:
            self._notification('%s (%s)' % (self.SETTINGS['ADDONLANGUAGE'](
                32103), self.SNAME[int(mode)]), self.SETTINGS['notify_maintenance'])
            self.LW.log(
                ['CHECK: This profile is disabled in addon settings - %s' % str(mode)], xbmc.LOGINFO)
            return False
        for key in self.SPROFILE:
            if self.SPROFILE[key]:
                success, loglines = checkPath(os.path.join(
                    self.SETTINGS['ADDONDATAPATH'], 'profile%s.json' % str(key)), createdir=False)
                self.LW.log(loglines)
                if not success:
                    self._notification('%s %s (%s)' % (self.SETTINGS['ADDONLANGUAGE'](32101), str(key), self.SNAME[key]),
                                       self.SETTINGS['notify_maintenance'])
                    self.LW.log(
                        ['PROFILE FILE does not exist for profile - %s' % str(key)], xbmc.LOGERROR)
                    return False
                self.APROFILE.append(str(key))

    def _convert(self, data):
        if sys.version_info < (3, 0):
            return data
        if isinstance(data, bytes):
            return data.decode()
        if isinstance(data, (str, int)):
            return str(data)
        if isinstance(data, dict):
            return dict(list(map(self._convert, list(data.items()))))
        if isinstance(data, tuple):
            return tuple(map(self._convert, data))
        if isinstance(data, list):
            return list(map(self._convert, data))
        if isinstance(data, set):
            return set(map(self._convert, data))

    def _get_enabled_profiles(self):
        enabled_profile_key = []
        enabled_profile_name = []
        for thekey, profile in self.SPROFILE.items():
            if profile:
                enabled_profile_key.append(thekey)
                enabled_profile_name.append(self.SNAME[thekey])
        return [enabled_profile_key, enabled_profile_name]

    def _notification(self, msg, display=True):
        if self.DISPLAYNOTIFICATION and display:
            self.DIALOG.notification(
                self.SETTINGS['ADDONLONGNAME'], msg, icon=self.SETTINGS['ADDONICON'], time=self.NOTIFYTIME)

    def _profile(self, profile):
        loglines, result = readFile(os.path.join(
            self.SETTINGS['ADDONDATAPATH'], 'profile%s.json' % profile))
        self.LW.log(loglines)
        try:
            jsonResult = json.loads(result)
        except ValueError:
            self._notification('%s %s (%s)' % (self.SETTINGS['ADDONLANGUAGE'](32104), profile, self.SNAME[int(profile)]),
                               self.SETTINGS['notify_maintenance'])
            self.LW.log(['LOAD JSON FROM FILE: Error reading from profile - %s' %
                        str(profile)], xbmc.LOGERROR)
            return False
        quote_needed = ['audiooutput.audiodevice',
                        'audiooutput.passthroughdevice',
                        'locale.audiolanguage',
                        'lookandfeel.soundskin']
        self.LW.log(['RESTORING SETTING: %s' %
                    self.SNAME[int(profile)]], xbmc.LOGINFO)
        for set_name, set_value in jsonResult.items():
            if not self.SETTINGS['player'] and set_name.startswith('videoplayer'):
                continue
            if not self.SETTINGS['video'] and set_name.startswith('videoscreen'):
                continue
            self.LW.log(['RESTORING SETTING: %s: %s' % (set_name, set_value)])
            # audiodelay is a float setting; restore it directly and skip the
            # generic Settings.SetSettingValue path which expects a quoted string
            if set_name == 'audiodelay':
                try:
                    delay_float = float(set_value)
                except (TypeError, ValueError):
                    delay_float = 0.0
                self.LW.log(['RESTORING AUDIODELAY: %s seconds' % delay_float], xbmc.LOGINFO)
                # During active playback, Settings.SetSettingValue is ignored for
                # audiodelay — must use Player.SetAudioDelay instead which talks
                # directly to the player instance. Fall back to Settings for when
                # no playback is active (e.g. switching profiles from the menu).
                if self.KODIPLAYER.isPlaying():
                    self.LW.log(['Using Player.SetAudioDelay (playback active)'], xbmc.LOGINFO)
                    xbmc.executeJSONRPC(
                        '{"jsonrpc": "2.0", "method": "Player.SetAudioDelay", "params": {"playerid": 1, "offset": %s}, "id": 1}' % delay_float)
                else:
                    self.LW.log(['Using Settings.SetSettingValue (no playback)'], xbmc.LOGINFO)
                    xbmc.executeJSONRPC(
                        '{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting": "audiodelay", "value": %s}, "id": 1}' % delay_float)
                continue
            if set_name in quote_needed:
                set_value = '"%s"' % set_value
            if self.SETTINGS['volume'] and set_name == 'volume':
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": %s}, "id": 1}' % jsonResult['volume'])
            else:
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting": "%s", "value": %s}, "id": 1}' % (set_name, set_value))
        # Unity volume / skin OSD hide — if this profile has unity_volume enabled,
        # force Kodi volume to 100 (0dB) so passthrough profiles never attenuate
        # signal regardless of codec, and set a skin boolean so the volume OSD
        # can be hidden in the skin XML via Skin.HasSetting(unity_volume_active).
        unity = self.SETTINGS.get('profile%s_unity' % profile, False)
        if unity:
            self.LW.log(['UNITY VOLUME: forcing volume to 100 for profile %s' % profile], xbmc.LOGINFO)
            xbmc.executeJSONRPC(
                '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": 100}, "id": 1}')
            # Set a home window property — readable from skin XML as
            # Window(10000).Property(unity_volume_active), works reliably
            # from script thread unlike Skin.SetBool via executebuiltin.
            xbmc.executebuiltin('Skin.SetBool(unity_volume_active)')
            import xbmcgui
            xbmcgui.Window(10000).setProperty('unity_volume_active', 'true')
        else:
            xbmc.executebuiltin('Skin.Reset(unity_volume_active)')
            import xbmcgui
            xbmcgui.Window(10000).setProperty('unity_volume_active', '')
        if self.AUTO:
            show_notification = self.SETTINGS['notify_auto']
        else:
            show_notification = self.SETTINGS['notify_manual']
        self._notification(self.SNAME[int(profile)], show_notification)
        success, loglines = writeFile(profile, os.path.join(
            self.SETTINGS['ADDONDATAPATH'], 'profile'), 'w')
        self.LW.log(loglines)
        s_cec = self.SETTINGS['profile%s_cec' % profile]
        if s_cec:
            self.LW.log(['SENDING CEC COMMAND: %s' %
                        self.CECCOMMANDS[s_cec]], xbmc.LOGINFO)
            xbmc.executebuiltin(self.CECCOMMANDS[s_cec])

    def _save(self):
        dialog_return, loglines = apdialog.Dialog().start(self.SETTINGS, title=self.SETTINGS['ADDONLANGUAGE'](32106),
                                                          buttons=self.ENABLEDPROFILES[1], force_dialog=True)
        self.LW.log(loglines)
        self.LW.log(['the returned value is %s' % str(dialog_return)])
        if dialog_return is None:
            return False
        else:
            button = self.ENABLEDPROFILES[0][dialog_return]
        # Prompt for audio delay manually — Kodi resets audiodelay to 0 when
        # playback stops, so we can't reliably read it from the running state
        # at save time. Ask the user to enter the value they dialled in.
        kb = xbmc.Keyboard('0.0', 'Audio delay in seconds (e.g. -0.275, or 0)')
        kb.doModal()
        if kb.isConfirmed():
            try:
                manual_audiodelay = float(kb.getText())
            except (ValueError, TypeError):
                manual_audiodelay = 0.0
        else:
            manual_audiodelay = None  # user cancelled — will fall back to live read
        settings_to_save = {}
        json_s = [
            '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"system","category":"audio"}},"id":1}',
            '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["volume"]}, "id": 1}',
            '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"player","category":"videoplayer"}}, "id":1}',
            '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"system","category":"display"}}, "id":1}'
        ]
        for j in json_s:
            json_get = xbmc.executeJSONRPC(j)
            json_get = json.loads(json_get)
            self.LW.log(['JSON: %s' % str(json_get)])
            if 'result' in json_get:
                if 'settings' in json_get['result']:
                    for theset in json_get['result']['settings']:
                        if 'value' in theset.keys():
                            if theset['value'] == True or theset['value'] == False:
                                settings_to_save[theset['id']] = str(
                                    theset['value']).lower()
                            else:
                                if isinstance(theset['value'], int):
                                    settings_to_save[theset['id']] = str(
                                        theset['value'])
                                else:
                                    settings_to_save[theset['id']] = str(
                                        theset['value']).encode('utf-8')

                if 'volume' in json_get['result']:
                    settings_to_save['volume'] = str(
                        json_get['result']['volume'])
        # Save audiodelay — prefer the manually entered value (entered above)
        # since Kodi resets audiodelay to 0 on playback stop. Fall back to
        # live JSON-RPC read only if the user cancelled the prompt.
        if manual_audiodelay is not None:
            settings_to_save['audiodelay'] = str(manual_audiodelay)
            self.LW.log(['SAVING AUDIODELAY (manual entry): %s seconds' % manual_audiodelay], xbmc.LOGINFO)
        else:
            audiodelay_response = xbmc.executeJSONRPC(
                '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "audiodelay"}, "id": 1}')
            try:
                audiodelay_result = json.loads(audiodelay_response)
                audiodelay_value = audiodelay_result.get('result', {}).get('value', 0.0)
                if audiodelay_value is None:
                    audiodelay_value = 0.0
                settings_to_save['audiodelay'] = str(float(audiodelay_value))
                self.LW.log(['SAVING AUDIODELAY (live read): %s seconds' % audiodelay_value], xbmc.LOGINFO)
            except (ValueError, KeyError, TypeError) as e:
                self.LW.log(['Could not read audiodelay (Kodi <21?): %s' % str(e)], xbmc.LOGWARNING)

        json_to_write = json.dumps(self._convert(settings_to_save))
        self.LW.log(['SAVING SETTING: %s' % self.SNAME[button]], xbmc.LOGINFO)
        success, loglines = writeFile(json_to_write, os.path.join(
            self.SETTINGS['ADDONDATAPATH'], 'profile%s.json' % str(button)), 'w')
        self.LW.log(loglines)
        if success:
            self._notification('%s %s (%s)' % (self.SETTINGS['ADDONLANGUAGE'](32102), str(button),
                                               self.SNAME[button]), self.SETTINGS['notify_maintenance'])

    def _toggle(self, mode):
        loglines, profile = readFile(os.path.join(
            self.SETTINGS['ADDONDATAPATH'], 'profile'))
        self.LW.log(loglines)
        if profile:
            if (len(self.APROFILE) == 1) or (profile not in self.APROFILE):
                profile = self.APROFILE[0]
            else:
                ip = int(self.APROFILE.index(profile))
                if len(self.APROFILE) == ip:
                    try:
                        profile = self.APROFILE[0]
                    except IndexError:
                        profile = self.APROFILE[0]
                else:
                    try:
                        profile = self.APROFILE[ip + 1]
                    except IndexError:
                        profile = self.APROFILE[0]
        else:
            profile = self.APROFILE[0]
        self._profile(profile)
