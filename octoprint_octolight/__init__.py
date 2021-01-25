# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import flask

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


class OctoLightPlugin(
	octoprint.plugin.StartupPlugin,
	octoprint.plugin.TemplatePlugin,
	octoprint.plugin.SimpleApiPlugin,
	octoprint.plugin.SettingsPlugin,
	octoprint.plugin.RestartNeedingPlugin
):
	light_state = False
	fan_state = false

	def get_settings_defaults(self):
		return dict(
			light_pin=13,
			fan_pin=15,
			inverted_light_output=False,
			inverted_fan_output=False
		)

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def on_after_startup(self):
		self.light_state = False
		self.fan_state = False
		self._logger.info("--------------------------------------------")
		self._logger.info("OctoLight started, listening for GET request")
		self._logger.info("Light: pin: {}, inverted_light_input: {}".format(
			self._settings.get(["light_pin"]),
			self._settings.get(["inverted_light_output"])
		))
		self._logger.info("Fan: pin: {}, inverted_input: {}".format(
			self._settings.get(["fan_pin"]),
			self._settings.get(["inverted_fan_output"])
		))
		self._logger.info("--------------------------------------------")

		# Setting the default state of pin
		GPIO.setup(int(self._settings.get(["light_pin"])), GPIO.OUT)
		if bool(self._settings.get(["inverted_light_output"])):
			GPIO.output(int(self._settings.get(["light_pin"])), GPIO.HIGH)
		else:
			GPIO.output(int(self._settings.get(["light_pin"])), GPIO.LOW)

		GPIO.setup(int(self._settings.get(["fan_pin"])), GPIO.OUT)
		if bool(self._settings.get(["inverted_fan_output"])):
			GPIO.output(int(self._settings.get(["fan_pin"])), GPIO.HIGH)
		else:
			GPIO.output(int(self._settings.get(["fan_pin"])), GPIO.LOW)

	def on_api_get(self, request):
		# Sets the GPIO every time, if user changed it in the settings.
		if request == "octolight":
			GPIO.setup(int(self._settings.get(["light_pin"])), GPIO.OUT)

			self.light_state = not self.light_state

			# Sets the light state depending on the inverted output setting (XOR)
			if self.light_state ^ self._settings.get(["inverted_light_output"]):
				GPIO.output(int(self._settings.get(["light_pin"])), GPIO.HIGH)
			else:
				GPIO.output(int(self._settings.get(["light_pin"])), GPIO.LOW)

			self._logger.info("Got request. Light state: {}".format(
				self.light_state
			))
		elif request == "octofan":
			GPIO.setup(int(self._settings.get(["fan_pin"])), GPIO.OUT)

			self.fan_state = not self.fan_state

			# Sets the light state depending on the inverted output setting (XOR)
			if self.fan_state ^ self._settings.get(["inverted_fan_output"]):
				GPIO.output(int(self._settings.get(["fan_pin"])), GPIO.HIGH)
			else:
				GPIO.output(int(self._settings.get(["fan_pin"])), GPIO.LOW)

			self._logger.info("Got request. Fan state: {}".format(
				self.fan_state
			))
		else:
			self._logger.info("Got incorrect request for: {}".format(
				request
			))

		return flask.jsonify(status="ok")

	def get_update_information(self):
		return dict(
			octolight=dict(
				displayName="OctoLight",
				displayVersion=self._plugin_version,

				type="github_release",
				current=self._plugin_version,

				user="gigibu5",
				repo="OctoLight",
				pip="https://github.com/gigibu5/OctoLight/archive/{target}.zip"
			)
		)


__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = OctoLightPlugin()

__plugin_hooks__ = {
	"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}
